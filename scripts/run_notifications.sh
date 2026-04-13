#!/usr/bin/env bash
set -euo pipefail
curl -sS http://127.0.0.1:8000/api/notifications/run | python3 -m json.tool
