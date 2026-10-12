#!/usr/bin/env bash
# Runs the four required experiments (Part J) by rebuilding the master with
# a different ARTIFICIAL_DELAY each time, letting each client sync a couple
# of times, then tearing everything down. Each client's container logs
# (captured with `docker compose logs`) contain the numbers for Part K's
# results table.
#
# Usage: ./run_experiments.sh

set -e

DELAYS=(0 0.1 0.2 0.5)
mkdir -p results

for d in "${DELAYS[@]}"; do
    echo ""
    echo "############################################################"
    echo "# Experiment with ARTIFICIAL_DELAY = ${d}s"
    echo "############################################################"

    export ARTIFICIAL_DELAY=$d

    docker compose down -v --remove-orphans 2>/dev/null || true
    ARTIFICIAL_DELAY=$d docker compose up --build -d

    # Let each client complete a couple of sync rounds.
    sleep 25

    logfile="results/experiment_delay_${d}s.log"
    docker compose logs --no-color > "$logfile"
    echo "Saved logs to $logfile"

    docker compose down -v --remove-orphans
done

echo ""
echo "All experiments complete. See the results/ directory for logs."
echo "Grep each log for 'Corrected Clock' and 'Final Error' to fill in Part K's table."
