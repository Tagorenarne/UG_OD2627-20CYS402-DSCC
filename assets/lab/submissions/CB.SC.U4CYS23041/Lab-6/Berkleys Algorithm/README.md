# Berkeley Clock Synchronization Algorithm

**20CYS402 &mdash; Distributed Systems and Cloud Computing &mdash; Lab #6B**

A coordinator-based clock synchronisation system built from five Docker
containers: one **master/coordinator** and four **clients**, joined by a
dedicated `clock-net` bridge network.

```
                       +----------------------+
                       |   MASTER /          |
                       |   COORDINATOR       |
                       |   Logical Clock     |
                       +----------+-----------+
                                  |
                         Docker Network
                             clock-net
                                  |
             +--------------------+--------------------+
             v                    v                    v
       +-----------+        +-----------+        +-----------+
       | Client 1  |        | Client 2  |        | Client 3  |
       |   -8 sec  |        |   +6 sec  |        |   -4 sec  |
       +-----------+        +-----------+        +-----------+
                                                       |
                                                       v
                                                 +-----------+
                                                 | Client 4  |
                                                 |  +10 sec  |
                                                 +-----------+
```

## Layout

```
clock-synchronization/
├── docker-compose.yml          master + 4 clients on the clock-net network
├── cs_ba_leader/               -> Docker Hub: santhoshtharun7/cs_ba_leader
│   ├── Dockerfile
│   ├── master.py               coordinator: poll, average, correct
│   ├── clock.py                shared clock + protocol helpers
│   └── README.md
├── cs_ba_follower/             -> Docker Hub: santhoshtharun7/cs_ba_follower
│   ├── Dockerfile
│   ├── client.py               participant: answer, accept correction
│   ├── clock.py                shared clock + protocol helpers
│   └── README.md
├── experiments/
│   └── run_experiments.sh      runs all five experiments, writes results/
└── results/                    captured master output per experiment
```

`clock.py` is duplicated in both build contexts on purpose: each Docker image
has to be buildable on its own, straight from its repository.

## Quick start

```bash
docker network create clock-net        # created automatically by compose too
docker compose up --build              # build and start all five nodes
docker ps                              # verify
docker network inspect clock-net       # inspect
docker compose logs clock-master       # read the synchronisation report
docker compose down -v                 # tear down
```

### Use the published images instead of building

```bash
docker compose pull
docker compose up
```

## Changing the clock offsets

Every offset is an environment variable, so no rebuild is needed:

```bash
CLIENT1_OFFSET=-15 CLIENT2_OFFSET=10 CLIENT3_OFFSET=-5 CLIENT4_OFFSET=20 \
    docker compose up
```

Or edit the `CLOCK_OFFSET` value of any service in `docker-compose.yml`.

## Output

```
  Step 2  |  Clock offsets relative to the master
  Node           Initial clock     Offset       RTT Status
  master            12:00:00.0       +0.0         - coordinator
  client1           11:59:52.0       -8.0   79.8ms ok
  client2           12:00:06.0       +6.0   82.9ms ok
  client3           11:59:56.0       -4.0   61.0ms ok
  client4           12:00:10.0      +10.0   64.0ms ok

  Step 3  |  Average offset (master included in the mean)
  (master=0  -8.0 +6.0 -4.0 +10.0)  /  5
  Average offset    : +0.8 sec

  Step 4  |  Corrections  =  average offset - node offset
  master      : +0.8 sec
  client1     : +8.8 sec
  client2     : -5.2 sec
  client3     : +4.8 sec
  client4     : -9.2 sec

  Step 6  |  Final clocks and synchronisation error
  Node             Final clock  Error vs master
  master            12:00:01.3           0.00 s
  client1           12:00:01.3          +0.04 s
  ...
  Max spread        : 11.0 ms
```

A Markdown results table is printed at the end of the run, ready to paste into
Part L of the report.

## Experiments

```bash
./experiments/run_experiments.sh          # all five
./experiments/run_experiments.sh exp4 exp5
```

| Tag | What it shows |
|---|---|
| `exp1` | hand-out Experiment 1: -5, +5, -3, +3 |
| `exp2` | hand-out Experiment 2: -15, +10, -5, +20 |
| `exp3` | our own offsets: -7, +12, -2, +9 |
| `exp4` | Part K: faulty clock at 15:30:00, **detection off** |
| `exp5` | Part K: same run, **outlier detection on** (threshold 60 s) |

The contrast between `exp4` and `exp5` is the interesting one:

| | `exp4` (classic Berkeley) | `exp5` (outlier detection) |
|---|---|---|
| Average offset | **+2520.6 s** | **+0.7 s** |
| Target time | 12:42:00.6 | 12:00:00.7 |
| client4 | dragged the whole group forward 42 minutes | excluded, left uncorrected |

A single bad clock inflates the mean of every honest node, so *all* the good
nodes get shifted. Excluding it is an **enhancement to the algorithm**, not part
of it.

## Results

### Experiment 1 &mdash; offsets -5, +5, -3, +3

| Node | Initial Clock | Offset | Average Offset | Correction | Final Clock | Error |
|---|---:|---:|---:|---:|---:|---:|
| Master | 12:00:00.0 | +0.0 | +0.0 | +0.0 | 12:00:00.0 | 0.000 |
| Client 1 | 11:59:55.0 | -5.0 | +0.0 | +5.0 | 12:00:00.0 | +0.040 |
| Client 2 | 12:00:05.0 | +5.0 | +0.0 | -5.0 | 12:00:00.0 | +0.040 |
| Client 3 | 11:59:57.0 | -3.0 | +0.0 | +3.0 | 12:00:00.0 | +0.038 |
| Client 4 | 12:00:03.0 | +3.0 | +0.0 | -3.0 | 12:00:00.0 | +0.028 |

The offsets cancel exactly, so the average is 0 and no node has to move.

### Experiment 2 &mdash; offsets -15, +10, -5, +20

| Node | Initial Clock | Offset | Average Offset | Correction | Final Clock | Error |
|---|---:|---:|---:|---:|---:|---:|
| Master | 12:00:00.0 | +0.0 | +2.0 | +2.0 | 12:00:02.0 | 0.000 |
| Client 1 | 11:59:45.0 | -15.0 | +2.0 | +17.0 | 12:00:02.0 | +0.049 |
| Client 2 | 12:00:10.0 | +10.0 | +2.0 | -8.0 | 12:00:02.0 | +0.037 |
| Client 3 | 11:59:55.0 | -5.0 | +2.0 | +7.0 | 12:00:02.0 | +0.034 |
| Client 4 | 12:00:20.0 | +20.0 | +2.0 | -18.0 | 12:00:02.0 | +0.019 |

Here the offsets do not cancel, so the whole group agrees on 12:00:02.0 &mdash;
correct relative to each other, but 2 s away from the coordinator's original
reading. That is the defining property of Berkeley: it guarantees **agreement**,
not accuracy.

### Experiment 3 &mdash; our own offsets: -7, +12, -2, +9

| Node | Initial Clock | Offset | Average Offset | Correction | Final Clock | Error |
|---|---:|---:|---:|---:|---:|---:|
| Master | 12:00:00.0 | +0.0 | +2.4 | +2.4 | 12:00:02.4 | 0.000 |
| Client 1 | 11:59:53.0 | -7.0 | +2.4 | +9.4 | 12:00:02.4 | +0.041 |
| Client 2 | 12:00:12.0 | +12.0 | +2.4 | -9.6 | 12:00:02.4 | +0.036 |
| Client 3 | 11:59:58.0 | -2.0 | +2.4 | +4.4 | 12:00:02.4 | +0.033 |
| Client 4 | 12:00:09.0 | +9.0 | +2.4 | -6.6 | 12:00:02.4 | +0.034 |

### Experiment 4 &mdash; faulty clock, detection **off**

Client 4 is set to 15:30:00, i.e. `CLOCK_OFFSET=+12600`.

| Node | Initial Clock | Offset | Average Offset | Correction | Final Clock | Error |
|---|---:|---:|---:|---:|---:|---:|
| Master | 12:00:00.0 | +0.0 | +2520.6 | +2520.6 | 12:42:00.6 | 0.000 |
| Client 1 | 11:59:55.0 | -5.0 | +2520.6 | +2525.6 | 12:42:00.6 | +0.045 |
| Client 2 | 12:00:05.0 | +5.0 | +2520.6 | +2515.6 | 12:42:00.6 | +0.035 |
| Client 3 | 12:00:03.0 | +3.0 | +2520.6 | +2517.6 | 12:42:00.6 | +0.037 |
| Client 4 | 15:30:00.0 | +12600.0 | +2520.6 | -10079.4 | 12:42:00.6 | +0.013 |

The four honest nodes, which were all within 5 s of the master, are all dragged
**42 minutes** forward. Client 4's error divided by 5 leaks into everybody.

### Experiment 5 &mdash; same run, detection **on** (`OUTLIER_THRESHOLD=60`)

| Node | Initial Clock | Offset | Average Offset | Correction | Final Clock | Error |
|---|---:|---:|---:|---:|---:|---:|
| Master | 12:00:00.0 | +0.0 | +0.7 | +0.7 | 12:00:00.7 | 0.000 |
| Client 1 | 11:59:55.0 | -5.0 | +0.7 | +5.8 | 12:00:00.8 | +0.043 |
| Client 2 | 12:00:05.0 | +5.0 | +0.7 | -4.2 | 12:00:00.8 | +0.045 |
| Client 3 | 12:00:03.0 | +3.0 | +0.7 | -2.2 | 12:00:00.8 | +0.033 |
| Client 4 | 15:30:00.0 | +12600.0 | +0.7 | excluded (faulty) | n/a | n/a |

The mean collapses back to +0.7 s and the healthy nodes stay near 12:00:00.8.
Client 4 is left uncorrected and flagged, because correcting a node we do not
trust would reintroduce the error.

> **Note.** Outlier rejection is an *implementation enhancement*, not part of
> the basic Berkeley algorithm. Classic Berkeley has no notion of a faulty
> node; `exp4` is what the unmodified algorithm actually does.

## Robustness

A node that does not answer is simply left out of that round &mdash; the rest
still synchronise:

```
  client3          UNREACHABLE        n/a       n/a !! no reply
  !! no reply from: client3, client4 - excluded from this round, the others still synchronise
  (master=0  -8.0 +6.0)  /  3
  Average offset    : -0.7 sec
```

This is verified by pointing the coordinator at hosts that do not exist; it
survives the round, reports the unreachable nodes distinctly from faulty ones,
and carries on.

## Accuracy

Every run ends with a `Max spread` line, typically 2&ndash;30 ms. Two sources:

1. The reply is generated at an unknown point inside the round trip, so even
   half-RTT compensation leaves a residual error. Disable it with
   `RTT_COMPENSATION=0` and the error roughly doubles.
2. In `frozen` mode the sample is exact by construction, so what remains is
   purely the transport.

The measured offsets in every run above match the configured offsets to within
0.001 s, confirming the algorithm itself is exact.

## Docker Hub

| Repository | Role |
|---|---|
| [`santhoshtharun7/cs_ba_leader`](https://hub.docker.com/r/santhoshtharun7/cs_ba_leader) | master / coordinator |
| [`santhoshtharun7/cs_ba_follower`](https://hub.docker.com/r/santhoshtharun7/cs_ba_follower) | client / follower node |

Both are `python:3.12-alpine`, standard library only, non-root, with health
checks. Image size is a few tens of MB.
