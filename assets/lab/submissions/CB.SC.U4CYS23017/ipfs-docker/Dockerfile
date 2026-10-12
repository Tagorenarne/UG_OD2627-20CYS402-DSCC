FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    wget \
    tar \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://dist.ipfs.tech/kubo/v0.31.0/kubo_v0.31.0_linux-arm64.tar.gz && \
    tar -xvzf kubo_v0.31.0_linux-arm64.tar.gz && \
    bash kubo/install.sh && \
    rm -rf kubo kubo_v0.31.0_linux-arm64.tar.gz

RUN ipfs init

WORKDIR /app

COPY sample.pdf .

EXPOSE 4001
EXPOSE 5001
EXPOSE 8080
EXPOSE 8081

CMD ["sh"]
