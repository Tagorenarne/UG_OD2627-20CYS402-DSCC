# =============================================================================
# cs_ba_leader  -  Berkeley Clock Synchronization :: MASTER / COORDINATOR
# 20CYS402 - Distributed Systems and Cloud Computing | Lab #6B
# =============================================================================
FROM python:3.12-alpine

LABEL org.opencontainers.image.title="cs_ba_leader" \
      org.opencontainers.image.description="Berkeley Clock Synchronization master/coordinator" \
      org.opencontainers.image.authors="santhoshtharun7" \
      org.opencontainers.image.version="1.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ID=master \
    CLOCK_OFFSET=0 \
    CLOCK_BASE=12:00:00 \
    CLOCK_MODE=frozen \
    CLOCK_TICK=0 \
    CLIENT_PORT=5000 \
    POLL_TIMEOUT=5 \
    POLL_MODE=parallel \
    RTT_COMPENSATION=1 \
    ROUNDS=1 \
    ROUND_INTERVAL=15 \
    OUTLIER_THRESHOLD=0 \
    OUTLIER_ACTION=skip \
    KEEP_ALIVE=0 \
    PRE_SYNC_DELAY=2

WORKDIR /app

# stdlib only - no dependency install step needed
COPY clock.py  master.py  ./

# Run as a non-root user (good practice; also keeps the container tidy)
RUN adduser -D -u 10001 berkeley && chown -R berkeley:berkeley /app
USER berkeley

EXPOSE 5000

# The coordinator is a client of the network: it dials out to the followers
# rather than listening, so liveness is simply "the process is still there".
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD pgrep -f "master.py" >/dev/null || exit 1

ENTRYPOINT ["python", "-u", "master.py"]
