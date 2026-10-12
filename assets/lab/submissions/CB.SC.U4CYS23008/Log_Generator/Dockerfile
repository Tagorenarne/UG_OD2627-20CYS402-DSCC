
FROM python:3.13-slim

WORKDIR /

RUN mkdir -p /data

RUN printf 'import time\nfrom datetime import datetime, timezone\n\nwhile True:\n    ts = datetime.now(timezone.utc).isoformat()\n    with open("/data/log.txt", "a") as f:\n        f.write(ts + "\\n")\n    print("Logged:", ts, flush=True)\n    time.sleep(5)\n' > /app.py

CMD ["python", "/app.py"]
