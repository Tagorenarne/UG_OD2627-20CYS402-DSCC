
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget tar ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ENV IPFS_VERSION=v0.28.0

RUN wget https://dist.ipfs.tech/kubo/${IPFS_VERSION}/kubo_${IPFS_VERSION}_linux-amd64.tar.gz && \
    tar -xvzf kubo_${IPFS_VERSION}_linux-amd64.tar.gz && \
    cd kubo && \
    bash install.sh && \
    cd .. && \
    rm -rf kubo kubo_${IPFS_VERSION}_linux-amd64.tar.gz

RUN ipfs --version

ENV IPFS_PATH=/data/ipfs-repo

WORKDIR /data

COPY sample.txt /data/sample.txt
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 4001/tcp
EXPOSE 5001/tcp
EXPOSE 8080/tcp

ENTRYPOINT ["/entrypoint.sh"]