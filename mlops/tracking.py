"""Local, reproducible MLflow tracking with no remote credentials."""
import math
from collections.abc import Mapping


def record_experiment(
    model_name: str,
    dataset_version: str,
    metrics: Mapping[str, float],
    *,
    tracking_uri: str,
) -> str:
    import mlflow

    if not model_name.strip() or not dataset_version.strip():
        raise ValueError("Model name and dataset version are required")
    if not metrics or any(
        isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value)
        for value in metrics.values()
    ):
        raise ValueError("Metrics must be non-empty and finite")

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("financial-research-offline")
    with mlflow.start_run(run_name=model_name) as run:
        mlflow.log_params({"model_name": model_name, "dataset_version": dataset_version})
        mlflow.log_metrics(dict(metrics))
        return run.info.run_id
