#!/usr/bin/env bash
# NetworkzeroMonitor - Mobile API server launcher (Unix)
# Ionity (Pty) Ltd - www.ionity.today
set -e
cd "$(dirname "$0")"

if [ -d "venv" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

# Host/port can be overridden, e.g. NZM_PORT=9000 ./run_mobile.sh
export NZM_HOST="${NZM_HOST:-0.0.0.0}"
export NZM_PORT="${NZM_PORT:-8088}"

echo "Open this on your phone (same Wi-Fi):"
echo "  http://$(hostname -I 2>/dev/null | awk '{print $1}'):${NZM_PORT}"
echo

exec python3 api_server.py
