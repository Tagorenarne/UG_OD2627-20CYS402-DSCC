 FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y wget tar

RUN wget https://dist.ipfs.tech/kubo/v0.38.1/kubo_v0.38.1_linux-arm64.tar.gz && \
    tar -xzf kubo_v0.38.1_linux-arm64.tar.gz && \
    cd kubo && \
    bash install.sh

WORKDIR /app

COPY sample.pdf /app/sample.pdf

CMD sh -c "ipfs init && ipfs add /app/sample.pdf"
