# =============================================================================
# cs_ba_follower  -  Berkeley Clock Synchronization :: CLIENT / FOLLOWER NODE
# 20CYS402 - Distributed Systems and Cloud Computing | Lab #6B
# =============================================================================
FROM python:3.12-alpine

LABEL org.opencontainers.image.title="cs_ba_follower" \
      org.opencontainers.image.description="Berkeley Clock Synchronization client/follower node" \
      org.opencontainers.image.authors="santhoshtharun7" \
      org.opencontainers.image.version="1.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CLIENT_ID=client \
    CLOCK_OFFSET=0 \
    CLOCK_BASE=12:00:00 \
    CLOCK_MODE=frozen \
    CLOCK_TICK=0 \
    PORT=5000

WORKDIR /app

# stdlib only - no dependency install step needed
COPY clock.py  client.py  ./

RUN adduser -D -u 10001 berkeley && chown -R berkeley:berkeley /app
USER berkeley

EXPOSE 5000

# Liveness: a client should always be able to accept a TCP connection
HEALTHCHECK --interval=15s --timeout=3s --start-period=3s --retries=3 \
    CMD python -c "import json,os,socket,sys; p=int(os.environ.get('PORT',5000)); s=socket.create_connection(('127.0.0.1',p),2); s.sendall((json.dumps({'cmd':'PING'})+'\n').encode()); d=s.recv(256); s.close(); sys.exit(0 if b'PONG' in d else 1)"

ENTRYPOINT ["python", "-u", "client.py"]
