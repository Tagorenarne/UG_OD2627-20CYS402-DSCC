# cs_ca_follower

Synchronizing client (the **follower** node) for a
[Cristian's Algorithm](https://en.wikipedia.org/wiki/Cristian%27s_algorithm)
clock-synchronization deployment.

The follower contacts the leader time server
([`santhoshtharun7/cs_ca_leader`](https://github.com/santhoshtharun7/cs_ca_leader))
over TCP and corrects its own clock using the round-trip time.

## The algorithm

```
T0   = local clock at request send
Ts   = timestamp returned by the leader
T1   = local clock at response receive

RTT  = T1 - T0
D    = RTT / 2                     (assumes symmetric one-way latency)
Tsync = Ts + D
θ    = Tsync - T1 = Ts - (T0 + T1)/2
```

The follower maintains a `VirtualClock` with an explicit `drift` value, so the
effect of each correction is visible and cumulative rather than hidden by the
host clock.

## Files

| File         | Purpose                                                       |
| ------------ | ------------------------------------------------------------- |
| `client.py`  | Runs the sync rounds and applies the computed offset           |
| `Dockerfile` | Builds the container image from `python:3.11-alpine`           |

## Configuration

All settings are environment variables, so no rebuild is needed to change them.

| Variable          | Default     | Meaning                                      |
| ----------------- | ----------- | -------------------------------------------- |
| `SERVER_HOST`     | `time-server` | Hostname/IP of the leader time server       |
| `SERVER_PORT`     | `8888`      | Port of the leader time server                |
| `SIMULATED_DRIFT` | `12.345678` | Initial local clock offset, in seconds       |
| `ROUNDS`          | `5`         | Number of synchronization rounds to run      |
| `INTERVAL`        | `3.0`       | Seconds to wait between rounds               |

`SIMULATED_DRIFT` is what makes the demo legible: the follower starts badly
wrong and visibly corrects itself toward the leader's clock.

## Build and run with Docker

```bash
docker build -t cs-ca-follower .
docker run --rm \
  -e SERVER_HOST=host.docker.internal \
  -e SIMULATED_DRIFT=12.345678 \
  -e ROUNDS=5 \
  cs-ca-follower
```

On Linux, `--add-host=host.docker.internal:host-gateway` is needed for the
host alias above. If the leader runs as a container on the same Docker network,
just pass its container/service name as `SERVER_HOST`.

## Run without Docker

```bash
SERVER_HOST=127.0.0.1 ROUNDS=5 python3 client.py
```

## Notes

- The client retries connecting up to 15 times with a 1.5 s pause, so it can be
  started at the same time as the leader and will wait for it to come up.
- Standard library only — no `requirements.txt` needed.
- `PYTHONUNBUFFERED=1` is set in the image so logs stream immediately.
