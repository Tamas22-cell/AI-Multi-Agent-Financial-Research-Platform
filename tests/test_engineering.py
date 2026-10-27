import json
import tempfile
import unittest
from pathlib import Path

from data.pipeline import export_validated_market_snapshot
from mlops.tracking import record_experiment
from observability import traced_span


class EngineeringTests(unittest.TestCase):
    def test_quality_gate_writes_only_valid_data(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "snapshot.json"
            result = export_validated_market_snapshot(
                {"BTC": {"price": 100.0, "change_pct": 2.0}}, path
            )
            self.assertEqual(result, {"accepted": 1, "rejected": 0})
            self.assertEqual(json.loads(path.read_text())["BTC"]["price"], 100.0)

    def test_quality_gate_does_not_write_invalid_records(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "snapshot.json"
            with self.assertRaises(ValueError):
                export_validated_market_snapshot(
                    {"BTC": {"price": -1.0, "change_pct": 2.0}}, path
                )
            self.assertFalse(path.exists())

    def test_opentelemetry_span_interface(self):
        with traced_span("offline.test"):
            pass

    def test_mlflow_records_reproducible_metadata(self):
        import mlflow
        with tempfile.TemporaryDirectory() as folder:
            uri = "sqlite:///" + str(Path(folder) / "mlruns.db")
            run_id = record_experiment(
                "baseline", "fixture-v1", {"accuracy": 0.8}, tracking_uri=uri
            )
            mlflow.set_tracking_uri(uri)
            run = mlflow.get_run(run_id)
            self.assertEqual(run.data.params["dataset_version"], "fixture-v1")
            self.assertAlmostEqual(run.data.metrics["accuracy"], 0.8)

    def test_mlflow_rejects_nan(self):
        with self.assertRaises(ValueError):
            record_experiment("baseline", "fixture-v1", {"accuracy": float("nan")}, tracking_uri="sqlite:///ignored.db")


if __name__ == "__main__":
    unittest.main()
