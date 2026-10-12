# Cristian's Clock Synchronization Algorithm in Docker

This project demonstrates **Cristian's Algorithm** for clock synchronization across distributed nodes using two separate Docker containers (one time server and one time client).

---

## 1. Algorithm Overview

In a distributed system, physical clocks on different machines tend to drift. Cristian's algorithm is a probabilistic method for synchronizing a client clock with a central time server.

### Mathematical Formulation
1. The client notes its local time before sending the request:
   $$T_0 = \text{Local Send Timestamp}$$
2. The server receives the request and returns its current time:
   $$T_{\text{server}} = \text{Server Timestamp}$$
3. The client receives the response and records its local time:
   $$T_1 = \text{Local Receive Timestamp}$$
4. **Round Trip Time (RTT)**:
   $$\text{RTT} = T_1 - T_0$$
5. **Estimated One-Way Latency** (assuming symmetric network delays):
   $$D = \frac{\text{RTT}}{2}$$
6. **Synchronized Time**:
   $$T_{\text{sync}} = T_{\text{server}} + D = T_{\text{server}} + \frac{T_1 - T_0}{2}$$
7. **Client Clock Offset** ($\theta$):
   $$\theta = T_{\text{sync}} - T_1 = T_{\text{server}} - \frac{T_0 + T_1}{2}$$

---

## 2. Project Architecture

- **`server/`**:
  - `server.py`: Listens on TCP port 8888, returns microsecond-precision server timestamp in JSON.
  - `Dockerfile`: Lightweight Python 3.11 Alpine container image.
- **`client/`**:
  - `client.py`: Implements Cristian's algorithm, tracks round-trip time, adjusts virtual clock drift, and verifies synchronization.
  - `Dockerfile`: Lightweight Python 3.11 Alpine container image.
- **`docker-compose.yml`**: Connects both containers via a dedicated bridge network `sync-net`.

---

## 3. Running with Docker Compose

Build and run both containers:
```bash
docker compose up --build
```

To run in detached mode and view client logs:
```bash
docker compose up --build -d
docker compose logs -f time-client
```

To shut down containers:
```bash
docker compose down
```
