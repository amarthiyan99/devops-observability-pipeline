#!/usr/bin/env bash
# Fastest path to a screen-recordable demo: app + Prometheus + Grafana,
# fully wired, via docker-compose. No Jenkins/K8s cluster required for
# this path — see k8s/ and ci/ for the full production-path deployment.
set -euo pipefail

echo "== 1. Run unit tests =="
cd app && python3 -m pip install --quiet -r requirements.txt && python3 -m pytest tests/ -v && cd ..

echo "== 2. Start the stack =="
docker compose -f monitoring/docker-compose.yml up --build -d

echo "== 3. Wait for services to be healthy =="
sleep 8
curl -sf http://localhost:8000/health && echo " -> app healthy"

echo "== 4. Generate load so dashboards/alerts have data =="
./scripts/load_test.sh 120 5 &

echo
echo "Grafana:    http://localhost:3000  (admin/admin)"
echo "Prometheus: http://localhost:9090"
echo "App:        http://localhost:8000"
echo
echo "In Prometheus, check Status -> Rules to see alert-rules.yml loaded."
echo "In Grafana, the 'Observability Demo Service' dashboard is auto-provisioned."
echo
echo "== Cleanup when done =="
echo "    docker compose -f monitoring/docker-compose.yml down -v"
