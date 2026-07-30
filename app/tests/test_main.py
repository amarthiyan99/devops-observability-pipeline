import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)


def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_work_returns_200_and_duration():
    resp = client.get("/work")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    assert "duration_ms" in body


def test_metrics_endpoint_exposes_prometheus_format():
    client.get("/work")  # generate at least one data point first
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "http_requests_total" in resp.text
    assert "http_request_duration_seconds" in resp.text


def test_error_endpoint_returns_valid_status_codes():
    # With randomized failure, just confirm it always returns one of the
    # two documented status codes rather than crashing.
    for _ in range(10):
        resp = client.get("/error")
        assert resp.status_code in (200, 500)


def test_error_metrics_increment_on_failure(monkeypatch):
    import main
    monkeypatch.setattr(main, "ERROR_RATE", 1.0)  # force failure deterministically
    resp = client.get("/error")
    assert resp.status_code == 500
    metrics_resp = client.get("/metrics")
    assert "app_errors_total" in metrics_resp.text
