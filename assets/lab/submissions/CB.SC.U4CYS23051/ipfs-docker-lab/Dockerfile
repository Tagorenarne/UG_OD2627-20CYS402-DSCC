# Start from a lightweight Linux base
FROM ubuntu:22.04

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install tools needed to download and extract the IPFS (kubo) binary
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget tar ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Download and install IPFS (kubo implementation)
ENV IPFS_VERSION=v0.28.0
RUN wget https://dist.ipfs.tech/kubo/${IPFS_VERSION}/kubo_${IPFS_VERSION}_linux-amd64.tar.gz && \
    tar -xvzf kubo_${IPFS_VERSION}_linux-amd64.tar.gz && \
    cd kubo && \
    bash install.sh && \
    cd .. && \
    rm -rf kubo kubo_${IPFS_VERSION}_linux-amd64.tar.gz

# Verify installation (fails the build early if something went wrong)
RUN ipfs --version

# IPFS repo location (used by the ipfs CLI itself)
ENV IPFS_PATH=/data/ipfs-repo

# Copy the sample file to upload and the entrypoint script
WORKDIR /data
COPY sample.txt /data/sample.txt
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose IPFS's default ports (API, Gateway, Swarm)
EXPOSE 4001 5001 8080

ENTRYPOINT ["/entrypoint.sh"]
