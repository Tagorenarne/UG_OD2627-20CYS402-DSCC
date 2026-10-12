FROM alpine:latest

# Install dependencies
RUN apk add --no-cache libc6-compat wget tar

# Download and install IPFS
RUN wget https://dist.ipfs.tech/kubo/v0.33.0/kubo_v0.33.0_linux-amd64.tar.gz && \
    tar -xvzf kubo_v0.33.0_linux-amd64.tar.gz && \
    bash kubo/install.sh && \
    rm -rf kubo kubo_v0.33.0_linux-amd64.tar.gz

# Initialize IPFS repository
ENV IPFS_PATH=/data/ipfs
RUN mkdir -p $IPFS_PATH && ipfs init

# Expose ports
EXPOSE 4001 5001 8080

# Start the IPFS daemon
CMD ["ipfs", "daemon"]
