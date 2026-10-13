FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV IPFS_VERSION=v0.30.0

RUN apt-get update && \
    apt-get install -y wget tar ca-certificates && \
    wget https://dist.ipfs.tech/kubo/${IPFS_VERSION}/kubo_${IPFS_VERSION}_linux-amd64.tar.gz && \
    tar -xvzf kubo_${IPFS_VERSION}_linux-amd64.tar.gz && \
    cd kubo && \
    bash install.sh && \
    rm -rf /var/lib/apt/lists/* kubo kubo_${IPFS_VERSION}_linux-amd64.tar.gz

COPY swarm.key /tmp/swarm.key
COPY sample.txt /sample.txt
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 4001 5001 8080

ENTRYPOINT ["/entrypoint.sh"]