# Cristian's Clock Synchronization Algorithm — Lab #6A

## 1. Project structure

```
clock-synchronization/
├── docker-compose.yml
├── run_experiments.sh
├── master/
│   ├── Dockerfile
│   └── master.py
└── client/
    ├── Dockerfile
    └── client.py
```

## 2. How it works

- **`master.py`** runs a TCP server on port 5000. For every `TIME_REQUEST` it
  receives, it optionally sleeps `ARTIFICIAL_DELAY` seconds (to simulate
  network/processing latency), then replies with its current time
  (`master_time`, treated as ground truth — offset 0).
- **`client.py`** simulates a machine whose clock is off by a constant
  `CLOCK_OFFSET` seconds. Every `SYNC_INTERVAL` seconds it:
  1. records `T1` on its own (skewed) clock,
  2. sends `TIME_REQUEST`,
  3. records `T2` on its own clock when the reply arrives,
  4. computes `RTT = T2 - T1`,
  5. estimates one-way delay as `RTT / 2`,
  6. computes `Corrected Clock = Master Time + RTT/2`,
  7. prints the full result block and (optionally) appends a row to a CSV.

## 3. Running it

```bash
cd clock-synchronization

# create the network (compose also creates it automatically, this is just
# to match Part A of the lab if you want to inspect it independently)
docker network create clock-net || true

# build and start everything
docker compose up --build
```

In another terminal:

```bash
docker ps
docker network inspect clock-net
docker compose logs -f clock-client2   # watch one client's sync output
```

Stop everything:

```bash
docker compose down
```

## 4. Running the four delay experiments (Part J)

```bash
chmod +x run_experiments.sh
./run_experiments.sh
```

This rebuilds the master with `ARTIFICIAL_DELAY` set to 0, 0.1, 0.2 and
0.5 seconds in turn, lets each client sync a couple of times, and saves
`docker compose logs` output to `results/experiment_delay_<d>s.log`. Pull the
`Corrected Clock` / `Final Error` / `RTT` / `Estimated Delay` lines out of
each log to fill in Part K's table.

You can also set a single client to log directly to CSV by adding
`RESULTS_FILE=/app/results.csv` to its environment and mounting a volume,
if you'd prefer structured output over grepping logs.

## 5. Draft answers — Part L questions

These are starting points; adapt them to what you actually observe in your
experiment logs.

1. **Why does Cristian's algorithm require a time server?**
   It's a client-pull, centralized algorithm — every client corrects its own
   clock against a single trusted reference (the master) rather than
   negotiating with peers, which keeps the protocol simple but makes the
   master a single point of truth (and failure).

2. **Why is RTT divided by two?**
   The algorithm assumes the request and response legs of the round trip
   take roughly equal time, so half of the measured round-trip delay is a
   reasonable estimate of the one-way delay between client and server.

3. **What assumption is made about network delay?**
   That it is (approximately) symmetric — the outbound request and the
   inbound response experience similar latency.

4. **What happens when the network delay increases?**
   RTT grows, so the *uncertainty* in the estimated one-way delay grows too
   (the true one-way delay could reasonably be anywhere in a wider range
   around RTT/2), which can increase synchronization error — even though the
   algorithm still applies the same RTT/2 correction.

5. **What happens if the request and response delays are asymmetric?**
   The RTT/2 estimate becomes biased: if the response leg is slower than the
   request leg (or vice versa), the corrected clock will be off by roughly
   half the difference between the two legs, in the direction of whichever
   leg was actually slower.

6. **Why should the actual OS clock not be modified for this experiment?**
   Changing the real system clock could break other running processes,
   logging, TLS certificate validation, cron jobs, etc. on the host, and
   could also make timestamps non-monotonic. It's safer (and sufficient for
   the lab) to simulate offsets in application-level variables.

7. **What happens if the master becomes unavailable?**
   Clients can't complete a sync — in this implementation, the connection
   attempt fails/times out, the client logs the failure, keeps running on
   its last (possibly still-skewed) clock, and retries on the next interval.
   In a real deployment you'd want a backup/secondary time server.

8. **Difference between initial logical clock and corrected logical clock?**
   The initial clock is the client's own, possibly skewed value
   (`real time + CLOCK_OFFSET`); the corrected clock is the value computed
   from the master's authoritative time plus the estimated one-way delay,
   which should be close to true time regardless of the client's original
   skew.

9. **How does the number of clients affect the master?**
   Each additional client adds concurrent connection/request load; since
   this master spawns a thread per connection, it scales reasonably for a
   handful of clients, but a very large number of simultaneous requests
   would increase queueing delay at the master, which in turn increases RTT
   and reduces synchronization accuracy for everyone.

10. **Limitations of Cristian's algorithm in a real distributed system?**
    Single point of failure (one time server), accuracy degrades under
    variable/asymmetric network delay, it doesn't handle Byzantine or
    faulty time servers (no fault tolerance / voting like Berkeley's
    algorithm or NTP's multi-source approach), and it only gives one-shot
    corrections rather than continuously disciplining the clock's drift
    rate.

## 6. Results table template (Part K)

Fill this in from the experiment logs:

| Experiment | Client | Initial Clock | RTT (ms) | Estimated Delay (ms) | Corrected Clock | Final Error (ms) |
|---|---|---:|---:|---:|---:|---:|
| 1 (0ms) | Client-1 | | | | | |
| 1 (0ms) | Client-2 | | | | | |
| 1 (0ms) | Client-3 | | | | | |
| 1 (0ms) | Client-4 | | | | | |
| 2 (100ms) | Client-1 | | | | | |
| 2 (100ms) | Client-2 | | | | | |
| 2 (100ms) | Client-3 | | | | | |
| 2 (100ms) | Client-4 | | | | | |
| 3 (200ms) | Client-1 | | | | | |
| 3 (200ms) | Client-2 | | | | | |
| 3 (200ms) | Client-3 | | | | | |
| 3 (200ms) | Client-4 | | | | | |
| 4 (500ms) | Client-1 | | | | | |
| 4 (500ms) | Client-2 | | | | | |
| 4 (500ms) | Client-3 | | | | | |
| 4 (500ms) | Client-4 | | | | | |
