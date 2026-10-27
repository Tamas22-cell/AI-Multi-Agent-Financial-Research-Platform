import json
import tempfile
import unittest
import os
import sys
import types
from contextlib import nullcontext
from unittest.mock import patch
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

    def test_langfuse_requires_explicit_opt_in_and_credentials(self):
        with patch.dict(os.environ, {"LANGFUSE_TRACING_ENABLED": "1"}, clear=True):
            with traced_span("offline.no-credentials"):
                pass

    def test_langfuse_observation_without_sensitive_payload(self):
        called = []
        class FakeClient:
            def start_as_current_observation(self, **kwargs):
                called.append(kwargs)
                return nullcontext()

        fake = types.ModuleType("langfuse")
        fake.get_client = lambda: FakeClient()
        env = {
            "LANGFUSE_TRACING_ENABLED": "1",
            "LANGFUSE_PUBLIC_KEY": "test-public",
            "LANGFUSE_SECRET_KEY": "test-secret",
            "LANGFUSE_BASE_URL": "http://localhost:3000",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch.dict(sys.modules, {"langfuse": fake}):
                with traced_span("financial.api.analyze"):
                    pass
        self.assertEqual(called, [{"name": "financial.api.analyze", "as_type": "span"}])
        self.assertNotIn("test-secret", repr(called))

    def test_langfuse_failure_falls_back_to_noop(self):
        fake = types.ModuleType("langfuse")
        fake.get_client = lambda: (_ for _ in ()).throw(RuntimeError("offline"))
        with patch.dict(os.environ, {
            "LANGFUSE_TRACING_ENABLED": "1",
            "LANGFUSE_PUBLIC_KEY": "test-public",
            "LANGFUSE_SECRET_KEY": "test-secret",
            "LANGFUSE_BASE_URL": "http://localhost:3000",
        }, clear=True), patch.dict(sys.modules, {"langfuse": fake}):
            with traced_span("offline.failure"):
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
