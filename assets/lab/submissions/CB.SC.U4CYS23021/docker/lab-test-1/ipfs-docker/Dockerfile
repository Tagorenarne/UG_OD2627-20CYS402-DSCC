FROM python:3.12-slim

ENV IPFS_VERSION=v0.32.0

RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/* && \
    curl --http1.1 -sSLo kubo.tar.gz https://dist.ipfs.tech/kubo/${IPFS_VERSION}/kubo_${IPFS_VERSION}_linux-amd64.tar.gz && \
    tar -xzf kubo.tar.gz && mv kubo/ipfs /usr/local/bin/ipfs && rm -rf kubo kubo.tar.gz && \
    ipfs init && \
    ipfs config Addresses.API /ip4/0.0.0.0/tcp/5001 && \
    ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080

COPY cys23021.txt /cys23021.txt

EXPOSE 4001 5001 8080

ENTRYPOINT ["/bin/sh", "-c", "ipfs daemon & until ipfs id > /dev/null 2>&1; do sleep 0.5; done && ipfs add /cys23021.txt && wait"]
