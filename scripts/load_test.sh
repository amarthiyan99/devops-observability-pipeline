#!/usr/bin/env bash
# Generates traffic against the local demo stack so the Grafana dashboard
# actually has data to show and the HighErrorRate / HighLatencyP95 alerts
# have a chance to fire during a demo recording.
#
# Usage: ./scripts/load_test.sh [duration_seconds] [requests_per_second]
set -euo pipefail

DURATION="${1:-120}"
RPS="${2:-5}"
APP_URL="${APP_URL:-http://localhost:8000}"

echo "Load-testing $APP_URL for ${DURATION}s at ~${RPS} req/s"
echo "Mix: 60% /work, 40% /error — watch Grafana at http://localhost:3000"

END=$((SECONDS + DURATION))
SLEEP_INTERVAL=$(awk "BEGIN {print 1/$RPS}")

while [ $SECONDS -lt $END ]; do
    if [ $((RANDOM % 10)) -lt 6 ]; then
        curl -s -o /dev/null "$APP_URL/work" &
    else
        curl -s -o /dev/null "$APP_URL/error" &
    fi
    sleep "$SLEEP_INTERVAL"
done

wait
echo "Load test complete."
