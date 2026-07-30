"""
Sample instrumented microservice — the deliberately-simple app this whole
pipeline exists to build, deploy, and observe. Not the point of the
project; the CI/CD + monitoring around it is.

Endpoints:
  GET  /health   — liveness/readiness probe target for K8s
  GET  /work     — simulates variable-latency work (for latency dashboards/alerts)
  GET  /error    — has a tunable failure rate (for error-rate dashboards/alerts)
  GET  /metrics  — Prometheus scrape target
"""
import os
import random
import time

from fastapi import FastAPI, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

app = FastAPI(title="observability-demo-service")

# -- Metrics ----------------------------------------------------------------
# Deliberately hand-instrumented (rather than an auto-instrumentation
# middleware) so it's obvious in the code exactly what's being measured and
# why — useful to be able to explain line-by-line in an interview.

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency in seconds", ["endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)
ERROR_COUNT = Counter(
    "app_errors_total", "Total application errors", ["endpoint", "error_type"]
)

# Failure rate for /error is configurable via env var so the load-test
# script (scripts/load_test.sh) can dial it up to actually trip alert
# thresholds during a demo, without redeploying the app.
ERROR_RATE = float(os.environ.get("ERROR_RATE", "0.1"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/work")
def work():
    endpoint = "/work"
    start = time.time()
    # Simulate realistic variable latency: mostly fast, occasionally slow —
    # a log-normal-ish shape rather than uniform, closer to real traffic.
    delay = min(random.expovariate(8), 3.0)
    time.sleep(delay)
    duration = time.time() - start
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    REQUEST_COUNT.labels(endpoint=endpoint, status="200").inc()
    return {"status": "completed", "duration_ms": round(duration * 1000, 2)}


@app.get("/error")
def error():
    endpoint = "/error"
    start = time.time()
    if random.random() < ERROR_RATE:
        duration = time.time() - start
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(endpoint=endpoint, status="500").inc()
        ERROR_COUNT.labels(endpoint=endpoint, error_type="simulated_failure").inc()
        return Response(content='{"error": "simulated failure"}', status_code=500,
                         media_type="application/json")
    duration = time.time() - start
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    REQUEST_COUNT.labels(endpoint=endpoint, status="200").inc()
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(
            content='{"error": "simulated failure"}',
            status_code=500,
            media_type="application/json",
        )
