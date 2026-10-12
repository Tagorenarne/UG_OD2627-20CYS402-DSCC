# cs_ca_leader

Reference time server (the **leader** node) for a
[Cristian's Algorithm](https://en.wikipedia.org/wiki/Cristian%27s_algorithm)
clock-synchronization deployment.

Followers ([`santhoshtharun7/cs_ca_follower`](https://github.com/santhoshtharun7/cs_ca_follower))
open a TCP connection, send a request, and receive the leader's timestamp back
as JSON. The follower then corrects its own clock using
`T_sync = T_server + RTT/2`.

## Files

| File         | Purpose                                                     |
| ------------ | ----------------------------------------------------------- |
| `server.py`  | TCP time server on port `8888`; replies with a JSON timestamp |
| `Dockerfile` | Builds the container image from `python:3.11-alpine`         |

## Behaviour

- Listens on `0.0.0.0:8888` with `SO_REUSEADDR`.
- Accepts connections serially in a loop, one request per connection.
- Captures its timestamp **immediately** on `recv` and returns:

  ```json
  {
    "server_time": 1759046400.123456,
    "server_time_str": "2025-09-28 21:20:00.123456"
  }
  ```

- Timestamps are microsecond-precision and returned as both a float epoch and
  a human-readable string.

## Build and run with Docker

```bash
docker build -t cs-ca-leader .
docker run -d --name cs-ca-leader -p 8888:8888 cs-ca-leader
docker logs -f cs-ca-leader
```

Verify it responds:

```bash
# from the host
python3 -c "import socket;s=socket.create_connection(('127.0.0.1',8888));s.sendall(b'TIME_REQ');print(s.recv(1024).decode())"
```

Stop and clean up:

```bash
docker rm -f cs-ca-leader
```

## Run without Docker

```bash
python3 server.py
```

## Notes

- The container needs no `requirements.txt` — the server uses only the Python
  standard library.
- `PYTHONUNBUFFERED=1` is set in the image so logs stream immediately under
  `docker logs`.
- Time is read with `time.time()` (wall clock), which is the clock followers
  are trying to agree on.
