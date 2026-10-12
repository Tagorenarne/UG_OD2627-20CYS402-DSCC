# 20CYS402 - Distributed Systems and Cloud Computing
![](https://img.shields.io/badge/Batch-23CYS-gold) ![](https://img.shields.io/badge/UG-blue) ![](https://img.shields.io/badge/Subject-DSCC-blue) <br/>

## Lab#6B - Berkeley Clock Synchronization Algorithm
![](https://img.shields.io/badge/Date-28_September-blue)

### 1. Objective

Implement the **Berkeley Clock Synchronization Algorithm** using multiple Docker containers representing distributed nodes and publish the container images to Docker Hub (`jaiaditya29/berkeley_algorithm`).

The implementation contains:

- **1 Master / Time Coordinator container** (`berkeley-master`)
- **4 Slave containers** (`berkeley-slave1` through `berkeley-slave4`)
- A dedicated Docker bridge network (`berkeley-net`)
- Configurable logical clock offsets on each node
- Active master polling mechanism
- Round Trip Time (RTT) measurement and latency compensation
- Average cluster offset calculation and individual adjustment dissemination
- Clock convergence verification

---

### 2. Expected Architecture

```text
                    +---------------------------+
                    |       Master Node         |
                    |   (Active Coordinator)    |
                    |       Offset: 0.0s        |
                    +-------------+-------------+
                                  |
                      Docker Network: berkeley-net
                                  |
          +-----------------------+-----------------------+
          |                       |                       |
          v                       v                       v
   +---------------+       +---------------+       +---------------+
   |    Slave 1    |       |    Slave 2    |       |    Slave 3    |
   |  Clock: -8s   |       |  Clock: +6s   |       |  Clock: -4s   |
   |  Port: 6000   |       |  Port: 6000   |       |  Port: 6000   |
   +---------------+       +---------------+       +---------------+
                                                          |
                                                          v
                                                   +---------------+
                                                   |    Slave 4    |
                                                   |  Clock: +10s  |
                                                   |  Port: 6000   |
                                                   +---------------+
```

---

### 3. Comparison: Cristian's vs Berkeley Algorithm

| Feature | Cristian's Algorithm | Berkeley Algorithm |
|---|---|---|
| **Initiator** | Client (Passive Server) | Master (Active Coordinator) |
| **Reference Time** | External UTC time source | Internal cluster average time |
| **Adjustment** | Client sets time to Master + RTT/2 | Master sends relative $\pm \Delta$ to each node |
| **Centralization** | Centralized | Centralized internal sync |
| **Fault Tolerance** | Single point of failure (UTC source) | Fault-tolerant average (outlier rejection) |

---

### 4. Mathematical Formulation

#### Step 1: Master Polls Each Slave
For each slave $i$:
1. Master records time before transmission: $T_1$
2. Master sends `POLL` request to slave.
3. Slave reads its current logical clock: $T_{\text{slave}}$ and replies.
4. Master records response arrival time: $T_2$

#### Step 2: Latency and Offset Estimation
- **Round-Trip Time**:
  $$RTT_i = T_2 - T_1$$
- **Estimated One-Way Delay**:
  $$D_i = \frac{RTT_i}{2}$$
- **Estimated Slave Clock at Master instant $T_2$**:
  $$T'_{\text{slave}, i} = T_{\text{slave}, i} + D_i$$
- **Clock Difference (Offset) of Slave $i$ relative to Master**:
  $$\Delta_i = T'_{\text{slave}, i} - T_2 = T_{\text{slave}, i} + \frac{RTT_i}{2} - T_2$$
- For the Master node itself:
  $$\Delta_{\text{master}} = 0$$

#### Step 3: Compute Cluster Average Offset
For a cluster of $M$ slaves and 1 master (total $N = M + 1$ nodes):
$$\mu = \frac{\Delta_{\text{master}} + \sum_{i=1}^M \Delta_i}{N}$$

#### Step 4: Calculate Individual Adjustments
- For each slave $i$:
  $$\text{Adj}_i = \mu - \Delta_i$$
- For the master node:
  $$\text{Adj}_{\text{master}} = \mu - 0 = \mu$$

#### Step 5: Clock Adjustment & Convergence
- Each node applies its adjustment:
  $$T_{\text{new}, i} = T_{\text{current}, i} + \text{Adj}_i$$
- All nodes in the cluster converge to the synchronized average time:
  $$T_{\text{target}} = T_{\text{master}} + \mu$$

---

### 5. Project Structure

```text
/Users/jaiaditya/Desktop/sem_7/dscc/
│
├── Berkeley_Algorithm.md         # Lab Documentation & Reference
├── berkeley_sync.py              # Standalone local simulator
│
└── berkeley-clock-sync/          # Dockerized Distributed System
    ├── docker-compose.yml
    ├── README.md
    ├── master/
    │   ├── Dockerfile
    │   └── master.py
    └── slave/
        ├── Dockerfile
        └── slave.py
```

---

### 6. Docker Environment Configuration

#### Containers and Offsets

| Container | Image Tag | Role | Initial Offset | Port |
|---|---|---|---:|---:|
| `berkeley-master` | `jaiaditya29/berkeley_algorithm:master` | Master Coordinator | 0.0 s | - |
| `berkeley-slave1` | `jaiaditya29/berkeley_algorithm:slave` | Slave Daemon | -8.0 s | 6000 |
| `berkeley-slave2` | `jaiaditya29/berkeley_algorithm:slave` | Slave Daemon | +6.0 s | 6000 |
| `berkeley-slave3` | `jaiaditya29/berkeley_algorithm:slave` | Slave Daemon | -4.0 s | 6000 |
| `berkeley-slave4` | `jaiaditya29/berkeley_algorithm:slave` | Slave Daemon | +10.0 s | 6000 |

---

### 7. Execution Commands

#### Run with Docker Compose
```bash
cd /Users/jaiaditya/Desktop/sem_7/dscc/berkeley-clock-sync
docker compose up --build
```

#### Docker Hub Repository
Repository: [`jaiaditya29/berkeley_algorithm`](https://hub.docker.com/r/jaiaditya29/berkeley_algorithm)

Published Tags:
- `jaiaditya29/berkeley_algorithm:master`
- `jaiaditya29/berkeley_algorithm:slave`
- `jaiaditya29/berkeley_algorithm:latest`
- `jaiaditya29/berkeley_algorithm:leader`
- `jaiaditya29/berkeley_algorithm:follower`
- `jaiaditya29/berkeley_algorithm:client`

---

### 8. Questions and Analysis

1. **Why does the Berkeley algorithm use an internal average rather than an absolute time source?**
   - The primary goal of internal synchronization is to keep all nodes in agreement with one another so that distributed ordering and consistency are preserved, even if connection to an external UTC time standard is unavailable.
2. **Why does the master send adjustments rather than the new absolute time?**
   - Sending adjustments avoids setting clocks backwards, which would break causality and timestamps of running processes (monotonicity guarantees).
3. **What is the effect of asymmetric network delays?**
   - Asymmetric delays introduce an estimation error of $\frac{|D_{\text{forward}} - D_{\text{backward}}|}{2}$ in offset calculation.
4. **How does Berkeley handle faulty or malicious nodes?**
   - Fault-tolerant averaging discards readings from nodes whose clock offsets deviate from the median by more than a specified threshold.
