#!/usr/bin/env bash
# =============================================================================
# run_experiments.sh
# 20CYS402 - Lab #6B - Berkeley Clock Synchronization
#
# Runs every experiment from the hand-out, captures the master's output into
# results/ and prints a summary table.
#
#   ./run_experiments.sh              run all experiments
#   ./run_experiments.sh exp1 exp3    run only the named ones
# =============================================================================
set -uo pipefail

cd "$(dirname "$0")/.."
PROJECT="berkeley-clock"
OUT_DIR="results"
mkdir -p "$OUT_DIR"

# --- offsets for each experiment -------------------------------------------
# client1 client2 client3 client4
declare -A EXP1=([-5]=[+5] [-3]=[+3])                       # hand-out Exp 1
declare -A EXP2=([-15]=[+10] [-5]=[+20])                    # hand-out Exp 2
declare -A EXP3=([-7]=[+12] [-2]=[+9])                      # our own offsets
# Hand-out Part K: client4 is grossly wrong (12:00:00 + 3.5 h = 15:30:00)
declare -A EXP4=([-5]=[+5] [+3]=[+12600])
declare -A EXP5=([-5]=[+5] [+3]=[+12600])                   # same, faults removed

hr() { printf '=%.0s' {1..78}; echo; }

run_one() {
    local tag="$1" c1="$2" c2="$3" c3="$4" c4="$5" threshold="$6" note="$7"
    local log="$OUT_DIR/${tag}.log"

    hr
    echo "  $tag  ->  client1=$c1  client2=$c2  client3=$c3  client4=$c4"
    [ "$threshold" != "0" ] && echo "  outlier threshold: +/-${threshold}s"
    echo "  $note"
    hr

    docker compose -p "$PROJECT" down -v >/dev/null 2>&1

    CLIENT1_OFFSET="$c1" CLIENT2_OFFSET="$c2" \
    CLIENT3_OFFSET="$c3" CLIENT4_OFFSET="$c4" \
    OUTLIER_THRESHOLD="$threshold" OUTLIER_ACTION=skip \
    docker compose -p "$PROJECT" up -d >/dev/null 2>&1

    # wait for the coordinator to finish its round
    for _ in $(seq 1 40); do
        sleep 1
        state=$(docker inspect -f '{{.State.Status}}' "${PROJECT}-clock-master-1" 2>/dev/null)
        [ "$state" = "exited" ] && break
    done

    docker compose -p "$PROJECT" logs --no-log-prefix clock-master \
        > "$log" 2>&1
    docker compose -p "$PROJECT" logs --no-log-prefix clock-client4 \
        >> "$log" 2>&1

    # strip the Step 1 "waiting" noise, show what matters
    sed -n '/Step 2/,$p' "$log" | head -60
    echo
    echo "  full log: $log"
    echo
}

selected=("$@")
want() {
    [ ${#selected[@]} -eq 0 ] && return 0
    for s in "${selected[@]}"; do [ "$s" = "$1" ] && return 0; done
    return 1
}

want exp1 && run_one "experiment1"  -5  5  -3  3  0 \
    "Part J, Experiment 1 - different clock offsets"
want exp2 && run_one "experiment2" -15 10 -5 20 0 \
    "Part J, Experiment 2 - wider spread of offsets"
want exp3 && run_one "experiment3"  -7 12 -2  9 0 \
    "Part J, Experiment 3 - our own offsets"
want exp4 && run_one "experiment4-faulty-no-detection" -5 5 3 12600 0 \
    "Part K - faulty clock, detection DISABLED (classic Berkeley)"
want exp5 && run_one "experiment5-faulty-detected"     -5 5 3 12600 60 \
    "Part K - same run, outlier detection ENABLED (+/-60s)"

hr
echo "  all experiments complete - logs in ./$OUT_DIR/"
docker compose -p "$PROJECT" down -v >/dev/null 2>&1
hr
