#!/usr/bin/env bash
# Elect, replicate, kill the leader, elect again, restart and back-fill.
# Needs curl only. Node N is published on port 800N.
set -e
cd "$(dirname "$0")"
PORTS="8001 8002 8003 8004 8005"

leader_port() {
  for p in $PORTS; do
    curl -sm1 localhost:$p/status 2>/dev/null | grep -q '"state": "leader"' && { echo "$p"; return; }
  done
}

show() { for p in $PORTS; do curl -sm1 localhost:$p/status || echo "(port $p down)"; echo; done; }

submit() { curl -s -X POST "localhost:$1/submit" -d "{\"cmd\":\"$2\"}"; echo; }

# --force-recreate so a cluster left running from a previous poke starts empty.
docker compose up -d --build --force-recreate
sleep 4

echo " --- final state ---"
show
echo "clean up with: docker compose down"
