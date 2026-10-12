# Berkeley Clock Synchronization Algorithm (Dockerized)

This project implements the **Berkeley Clock Synchronization Algorithm** in a distributed environment using Docker containers.

## Docker Hub Repository

The images are pushed to Docker Hub under:
- **Repository**: [`jaiaditya29/berkeley_algorithm`](https://hub.docker.com/r/jaiaditya29/berkeley_algorithm)
- **Tags**:
  - `master`, `leader`, `latest` (Master coordinator)
  - `slave`, `follower`, `client` (Slave daemon)

## Architecture

- **1 Master Coordinator (`berkeley-master`)**:
  - Actively polls all slave nodes for their logical clocks.
  - Measures Round Trip Time (RTT) and estimates one-way transmission latency ($D = RTT / 2$).
  - Computes the cluster average clock offset across all nodes:
    $$\mu = \frac{\Delta_{\text{master}} + \sum \Delta_{\text{slave}}}{N}$$
  - Calculates individual offset adjustments for each node ($\text{Adjustment}_i = \mu - \Delta_i$).
  - Disseminates the adjustments to all slaves and updates its own clock.
- **4 Slaves (`berkeley-slave1` to `berkeley-slave4`)**:
  - Passive daemons listening on port 6000.
  - Started with varying initial clock offsets (-8s, +6s, -4s, +10s).
  - Respond to master polling and apply received adjustments to synchronize their clocks.
- **Dedicated Bridge Network (`berkeley-net`)**

## Quick Start

### 1. Run with Docker Compose
```bash
cd berkeley-clock-sync
docker compose up --build
```

### 2. View Logs
View master synchronization summary:
```bash
docker logs berkeley-master
```

View individual slave logs:
```bash
docker logs berkeley-slave1
docker logs berkeley-slave2
```

### 3. Stop Containers
```bash
docker compose down
```

## Docker Images & Hub Push Commands

```bash
# Build images
docker build -t jaiaditya29/berkeley_algorithm:master ./master
docker build -t jaiaditya29/berkeley_algorithm:slave ./slave

# Push to Docker Hub
docker push jaiaditya29/berkeley_algorithm:master
docker push jaiaditya29/berkeley_algorithm:slave
docker push jaiaditya29/berkeley_algorithm:latest
```
