FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && \
    apt-get install -y wget tar ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Download and install IPFS (Kubo)
RUN wget https://dist.ipfs.tech/kubo/v0.32.1/kubo_v0.32.1_linux-amd64.tar.gz && \
    tar -xzf kubo_v0.32.1_linux-amd64.tar.gz && \
    cd kubo && \
    ./install.sh && \
    cd .. && \
    rm -rf kubo kubo_v0.32.1_linux-amd64.tar.gz

WORKDIR /app

COPY hello.txt .

CMD ipfs init && ipfs add hello.txt