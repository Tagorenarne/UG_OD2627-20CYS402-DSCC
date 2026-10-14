#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker is not installed or not in PATH." >&2
  exit 1
fi

echo ">>> Starting db connector compose stack"
docker compose -f "$ROOT_DIR/lab-test-1/db-connector/docker-compose.yml" up --build -d
docker compose -f "$ROOT_DIR/lab-test-1/db-connector/docker-compose.yml" ps

echo
echo ">>> Starting lab3 task1 compose stack"
docker compose -f "$ROOT_DIR/lab3/task1/docker-compose.yml" up -d
docker compose -f "$ROOT_DIR/lab3/task1/docker-compose.yml" ps

echo
echo ">>> Building lab1 image"
docker build -t cys-lab1 "$ROOT_DIR/lab1"
echo ">>> Replacing lab1 container"
docker rm -f lab1-nginx >/dev/null 2>&1 || true
docker run -d --name lab1-nginx -p 8081:80 cys-lab1 >/dev/null
docker ps --filter "name=^/lab1-nginx$" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo
echo ">>> Building lab2 task1 image"
docker build -t cys-lab2-task1 "$ROOT_DIR/lab2/task1"
echo ">>> Replacing lab2 task1 container"
docker rm -f lab2-task1 >/dev/null 2>&1 || true
docker run -d --name lab2-task1 -p 5000:5000 cys-lab2-task1 >/dev/null
docker ps --filter "name=^/lab2-task1$" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo
echo ">>> Building lab2 task2 image"
docker build -t cys-lab2-task2 "$ROOT_DIR/lab2/task2"
echo ">>> Replacing lab2 task2 container"
docker rm -f lab2-task2 >/dev/null 2>&1 || true
docker run -d --name lab2-task2 -p 8000:8000 cys-lab2-task2 >/dev/null
docker ps --filter "name=^/lab2-task2$" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo
echo ">>> Building IPFS image"
docker build -t cys-ipfs "$ROOT_DIR/lab-test-1/ipfs-docker"
echo ">>> Replacing IPFS container"
docker rm -f lab-ipfs >/dev/null 2>&1 || true
docker run -d --name lab-ipfs -p 4001:4001 -p 5001:5001 -p 8082:8080 cys-ipfs >/dev/null
docker ps --filter "name=^/lab-ipfs$" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo
cat <<'SUMMARY'
All requested labs have been launched.

Expected endpoints:
- lab3/task1 web:      http://localhost:8080
- lab1 nginx:          http://localhost:8081
- lab2/task1 flask:    http://localhost:5000
- lab2/task2 flask:    http://localhost:8000
- IPFS gateway:        http://localhost:8082
- IPFS API:            http://localhost:5001

Notes:
- The db-connector app is a one-shot container and may exit with code 0 after printing success.
- The loggen and logread containers are not started here because they are intentionally infinite loops.

Useful commands:
- docker ps -a
- docker logs db-connector
- docker logs lab2-task1
- docker logs lab2-task2
- docker logs lab-ipfs

To stop everything started by this script:
- ./stop-all.sh
SUMMARY
