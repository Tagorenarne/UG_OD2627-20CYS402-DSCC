#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ">>> Stopping compose stacks"
docker compose -f "$ROOT_DIR/lab-test-1/db-connector/docker-compose.yml" down || true
docker compose -f "$ROOT_DIR/lab3/task1/docker-compose.yml" down || true

echo
echo ">>> Removing standalone containers"
docker rm -f lab1-nginx lab2-task1 lab2-task2 lab-ipfs >/dev/null 2>&1 || true

echo
echo "All containers started by run-all.sh have been stopped."
