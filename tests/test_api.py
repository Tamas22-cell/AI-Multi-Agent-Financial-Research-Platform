import io
import json
import math
import unittest
from unittest.mock import patch

from api.analyze import _sanitize_json, handler


class HandlerHarness:
    def __init__(self, path):
        self.path = path
        self.wfile = io.BytesIO()
        self.status = None
        self.headers = {}

    def send_response(self, status):
        self.status = status

    def send_header(self, name, value):
        self.headers[name.lower()] = value

    def end_headers(self):
        pass

    _json_error = handler._json_error


class ApiTests(unittest.TestCase):
    def test_sanitize_json_removes_non_finite_nested_values(self):
        value = {"a": math.nan, "b": [math.inf, -math.inf, 1.5], "c": {"x": "ok"}}
        result = _sanitize_json(value)
        self.assertEqual(result, {"a": None, "b": [None, None, 1.5], "c": {"x": "ok"}})
        json.dumps(result, allow_nan=False)

    @patch("api.analyze.Orchestrator")
    def test_analyze_returns_json_without_network(self, orchestrator):
        orchestrator.return_value.run.return_value = {
            "decision": "HOLD", "market_score": math.nan, "agents": []
        }
        request = HandlerHarness("/api/analyze")
        handler.do_GET(request)
        self.assertEqual(request.status, 200)
        self.assertEqual(request.headers["content-type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(request.wfile.getvalue()), {
            "decision": "HOLD", "market_score": None, "agents": []
        })

    def test_unknown_route_is_404(self):
        request = HandlerHarness("/not-a-route")
        handler.do_GET(request)
        self.assertEqual(request.status, 404)
        self.assertEqual(request.wfile.getvalue(), b"Not found")

    @patch("api.analyze.Orchestrator")
    def test_agent_failure_returns_500_json(self, orchestrator):
        orchestrator.return_value.run.side_effect = RuntimeError("offline test failure")
        request = HandlerHarness("/api/analyze")
        handler.do_GET(request)
        self.assertEqual(request.status, 500)
        self.assertEqual(json.loads(request.wfile.getvalue())["status"], "error")


if __name__ == "__main__":
    unittest.main()
