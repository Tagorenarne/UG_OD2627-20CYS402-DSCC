# Raft Consensus Algorithm using Python & Docker

## Overview

This project is a simplified implementation of the Raft Consensus Algorithm using Python, Flask, and Docker.

The system consists of three Raft nodes running as Docker containers that communicate using HTTP-based RPCs.

It demonstrates the core concepts of distributed consensus including:

- Leader Election
- Heartbeats
- Leader Failover
- Log Replication
- Majority Commit
- Client Requests

---

## Architecture

                Client
                   │
                   ▼
            +--------------+
            |    Leader    |
            +--------------+
             /           \
            /             \
           ▼               ▼
     +-----------+   +-----------+
     | Follower  |   | Follower  |
     +-----------+   +-----------+

The leader replicates log entries to followers.

---

## Technologies Used

- Python 3
- Flask
- Docker
- Docker Compose
- Requests Library

---

## Project Structure

raft-python/
│
├── app/
│   ├── config.py
│   ├── node.py
│   ├── raft.py
│   └── server.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

---

## Features

### Leader Election

Nodes begin as Followers.

If no heartbeat is received, a node becomes a Candidate and requests votes.

The node receiving a majority becomes the Leader.

---

### Heartbeats

The Leader periodically sends heartbeats to Followers.

Followers reset their election timeout after receiving heartbeats.

---

### Leader Failover

If the Leader fails:

- Followers detect heartbeat timeout.
- A new election is started.
- A new Leader is elected automatically.

---

### Log Replication

Client commands are accepted only by the Leader.

Example:

SET x=10

The Leader:

1. Appends the entry locally.
2. Replicates it to Followers.
3. Waits for majority acknowledgement.
4. Commits the entry.

---

## Running the Project

Build the project:

docker compose build

Run the cluster:

docker compose up

---

## Testing Leader Election

Observe the logs.

Expected output:

node2 became CANDIDATE

node1 voted for node2

node3 voted for node2

******** node2 became LEADER ********

---

## Testing Failover

Stop the Leader:

docker stop node2

A new Leader should be elected automatically.

---

## Testing Log Replication

Send a client request to the Leader.

Example:

curl -X POST http://localhost:5001/client \
-H "Content-Type: application/json" \
-d '{"command":"SET x=10"}'

Expected output:

Replication ACKs = 3

Committed entry #1

---

## Verify Logs

curl http://localhost:5001/log

curl http://localhost:5002/log

curl http://localhost:5003/log

All nodes should contain the same replicated log.

---

## Future Improvements

- Persistent storage
- Log index and term
- Snapshotting
- Log conflict resolution
- Dynamic cluster membership
- State machine replication

---

## Author

Hiba Leeyakath S
CB.SC.U4CYS23017
B.Tech Cyber Security

