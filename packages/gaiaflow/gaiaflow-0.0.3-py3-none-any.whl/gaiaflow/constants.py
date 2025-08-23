from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass(frozen=True)
class Action:
    name: str


class BaseAction:
    START = Action("start")
    STOP = Action("stop")
    RESTART = Action("restart")
    CLEANUP = Action("cleanup")


class ExtendedAction:
    DOCKERIZE = Action("dockerize")
    CREATE_CONFIG = Action("create_config")
    CREATE_SECRET = Action("create_secret")
    UPDATE_DEPS = Action("update_deps")


GAIAFLOW_CONFIG_DIR = Path.home() / ".gaiaflow"
GAIAFLOW_CONFIG_DIR.mkdir(exist_ok=True)
GAIAFLOW_STATE_FILE = GAIAFLOW_CONFIG_DIR / "state.json"


class Service(str, Enum):
    airflow = "airflow"
    mlflow = "mlflow"
    minio = "minio"
    jupyter = "jupyter"
    all = "all"


AIRFLOW_SERVICES = [
    "airflow-apiserver",
    "airflow-scheduler",
    "airflow-init",
    "airflow-dag-processor",
    "airflow-triggerer",
    "postgres-airflow",
]

MLFLOW_SERVICES = ["mlflow", "postgres-mlflow"]

MINIO_SERVICES = ["minio", "minio_client"]

DEFAULT_MINIO_AWS_ACCESS_KEY_ID = "minio"
DEFAULT_MINIO_AWS_SECRET_ACCESS_KEY = "minio123"
DEFAULT_MLFLOW_TRACKING_URI = "http://localhost:5000"

# TODO: Talk with Tejas/Norman (currently contains random values)
RESOURCE_PROFILES = {
    "low": {
        "request_cpu": "250m",
        "limit_cpu": "500m",
        "request_memory": "512Mi",
        "limit_memory": "1Gi",
        "limit_gpu": "0",
    },
    "medium": {
        "request_cpu": "500m",
        "limit_cpu": "1",
        "request_memory": "1Gi",
        "limit_memory": "2Gi",
        "limit_gpu": "0",
    },
    "high": {
        "request_cpu": "1",
        "limit_cpu": "2",
        "request_memory": "2Gi",
        "limit_memory": "4Gi",
        "limit_gpu": "0.5",
    },
    "ultra": {
        "request_cpu": "2",
        "limit_cpu": "4",
        "request_memory": "4Gi",
        "limit_memory": "8Gi",
        "limit_gpu": "1",
    },
}

DEFAULT_IMAGE_NAME = "user-image:v1"
