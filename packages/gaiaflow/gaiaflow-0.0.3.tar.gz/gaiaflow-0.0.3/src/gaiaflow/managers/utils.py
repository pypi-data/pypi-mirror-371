import docker
import json
import subprocess
import sys
import tempfile
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import fsspec
import typer

from gaiaflow.constants import GAIAFLOW_STATE_FILE

fs = fsspec.filesystem("file")


def get_gaialfow_version() -> str:
    try:
        from importlib.metadata import version

        return version("gaiaflow")
    except Exception:
        print("Package not installed. Getting version from the pyproject.toml")
        import tomllib

        pyproject = tomllib.loads(Path("pyproject.toml").read_text())
        return pyproject["project"]["version"]


def find_python_packages(base_path: Path):
    outer_packages = []

    for child in base_path.iterdir():
        if child.is_dir() and (child / "__init__.py").exists():
            outer_packages.append(child.name)

    return outer_packages


def log_info(message: str):
    print(f"\033[0;34m[{datetime.now().strftime('%H:%M:%S')}]\033[0m {message}")


def log_error(message: str):
    print(f"\033[0;31mERROR:\033[0m {message}", file=sys.stderr)


def run(command: list, error_message: str, env=None):
    try:
        subprocess.call(command, env=env)
    except Exception:
        log_error(error_message)
        raise


def handle_error(message: str):
    log_error(f"Error: {message}")
    sys.exit(1)


def get_state_file() -> Path:
    return GAIAFLOW_STATE_FILE


def save_project_state(project_path: Path, gaiaflow_path: Path):
    state_file = get_state_file()
    try:
        if state_file.exists():
            with state_file.open("r") as f:
                state = json.load(f)
        else:
            state = {}
    except (json.JSONDecodeError, FileNotFoundError):
        state = {}

    project_path_str = str(project_path)
    gaiaflow_path_str = str(gaiaflow_path)
    keys_to_delete = [
        k
        for k, v in state.items()
        if v.get("project_path") == project_path_str and k != gaiaflow_path_str
    ]
    for k in keys_to_delete:
        del state[k]

    state[gaiaflow_path_str] = {
        "project_path": project_path_str,
    }

    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def load_project_state() -> dict | None:
    state_file = get_state_file()
    print("state_file", state_file)
    if not state_file.exists():
        return None

    try:
        with open(state_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def check_structure(base_path: Path, structure: dict) -> bool:
    for name, sub in structure.items():
        if name == "_files_":
            for file_name in sub:
                file_path = base_path / file_name
                if not file_path.exists():
                    typer.echo(f"Missing file: {file_path}", err=True)
                    return False
            continue

        path = base_path / name
        if not path.exists() or not path.is_dir():
            typer.echo(f"Missing folder: {path}", err=True)
            return False

        if isinstance(sub, dict):
            if not check_structure(path, sub):
                return False
        elif isinstance(sub, list):
            for item in sub:
                item_path = path / item
                if not item_path.exists():
                    typer.echo(f"Missing file: {item_path}", err=True)
                    return False
        else:
            raise TypeError("Structure values must be dict or list")
    return True


def gaiaflow_path_exists_in_state(gaiaflow_path: Path, check_fs: bool = True) -> bool:
    REQUIRED_STRUCTURE = {
        "docker_stuff": {
            "docker-compose": [
                "docker-compose.yml",
                "docker-compose-minikube-network.yml",
                "entrypoint.sh",
            ],
            "airflow": ["Dockerfile"],
            "mlflow": ["Dockerfile", "requirements.txt"],
            "user-package": ["Dockerfile"],
            "_files_": ["kube_config_inline"],
        }
    }
    state = load_project_state()
    if not state:
        return False

    key = str(gaiaflow_path)
    if key not in state:
        return False

    if check_fs:
        if not gaiaflow_path.exists():
            typer.echo(
                f"Gaiaflow path exists in state but not on disk: {gaiaflow_path}",
                err=True,
            )
            return False

        if not check_structure(gaiaflow_path, REQUIRED_STRUCTURE):
            return False

    return True


def delete_project_state(gaiaflow_path: Path):
    state_file = get_state_file()
    print("state_file", state_file)
    if not state_file.exists():
        log_error(
            "State file not found at ~/.gaiaflow/state.json. Please run the services."
        )
        return

    try:
        with open(state_file, "r") as f:
            state = json.load(f)

        print("found!", state.get("gaiaflow_path"), state)
        key = str(gaiaflow_path)
        if key in state:
            del state[key]
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)
    except (json.JSONDecodeError, FileNotFoundError, Exception):
        raise


def parse_key_value_pairs(pairs: list[str]) -> dict:
    data = {}
    for pair in pairs:
        if "=" not in pair:
            raise typer.BadParameter(f"Invalid format: '{pair}'. Expected key=value.")
        key, value = pair.split("=", 1)
        data[key] = value
    return data


def create_directory(dir_name):
    if not fs.exists(dir_name):
        try:
            fs.makedirs(dir_name, exist_ok=True)
            log_info(f"Created directory: {dir_name}")
        except Exception as e:
            handle_error(f"Failed to create {dir_name} directory: {e}")
    else:
        log_info(f"Directory {dir_name} already exists")

    set_permissions(dir_name)


def set_permissions(path, mode=0o777):
    try:
        fs.chmod(path, mode)
        log_info(f"Set permissions for {path}")
    except Exception:
        log_info(f"Warning: Could not set permissions for {path}")


def create_gaiaflow_context_path(project_path: Path) -> tuple[Path, Path]:
    user_project_path = Path(project_path).resolve()
    if not user_project_path.exists():
        raise FileNotFoundError(f"{user_project_path} not found")
    version = get_gaialfow_version()
    # project_name = str(user_project_path).split("/")[-1]
    project_name = user_project_path.name
    tmp_dir = Path(tempfile.gettempdir())
    gaiaflow_path =  tmp_dir / f"gaiaflow-{version}-{project_name}"

    return gaiaflow_path, user_project_path


def convert_crlf_to_lf(file_path: str):
    """
    Converts a file from Windows-style CRLF line endings to Unix-style LF line endings.

    Args:
        file_path (str): Path to the file to convert.
    """
    with open(file_path, "rb") as f:
        content = f.read()

    # Replace CRLF (\r\n) with LF (\n)
    new_content = content.replace(b"\r\n", b"\n")

    with open(file_path, "wb") as f:
        f.write(new_content)

    print(f"Converted {file_path} to LF line endings.")


def is_wsl() -> bool:
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False

def env_exists(env_name, env_tool="mamba"):
    result = subprocess.run(
        [env_tool, "env", "list", "--json"], capture_output=True, text=True
    )
    envs = json.loads(result.stdout).get("envs", [])
    return any(env_name in env for env in envs)

def update_micromamba_env_in_docker(
        containers: list[str],
        env_name: str = "default_user_env",
        max_workers: int = 4,
    ):
    client = docker.from_env()

    def _update_one(cname: str):
        try:
            container = client.containers.get(cname)
        except docker.errors.NotFound:
            log_error(f"Container '{cname}' not found. Skipping.")
            return

        cmd = f"micromamba install -y -n {env_name} -f /opt/airflow/environment.yml"
        log_info(f"[{cname}] Running command: {cmd}")
        exit_code, output = container.exec_run(cmd)

        if exit_code != 0:
            log_error(f"[{cname}] micromamba failed: {output.decode()}")
            return

        log_info(f"[{cname}] Updated successfully.")
        log_info(output.decode())

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_update_one, cname): cname for cname in containers
        }

        for future in as_completed(futures):
            cname = futures[future]
            try:
                future.result()
            except Exception as e:
                log_error(f"[{cname}] Unexpected error: {e}")