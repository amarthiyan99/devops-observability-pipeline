FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

RUN useradd -u 10001 -m appuser
USER 10001

EXPOSE 8000

# Container-level healthcheck mirrors the K8s liveness probe (see
# k8s/deployment.yaml) — useful for local docker-compose runs too, where
# there's no kubelet to do this for you.
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
