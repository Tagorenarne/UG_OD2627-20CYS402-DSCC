FROM alpine:latest

# Install dependencies
RUN apk add --no-cache wget tar bash libc6-compat

# Download and install Kubo (IPFS)
RUN wget https://dist.ipfs.tech/kubo/v0.33.0/kubo_v0.33.0_linux-amd64.tar.gz && \
    tar -xvzf kubo_v0.33.0_linux-amd64.tar.gz && \
    sh kubo/install.sh && \
    rm -rf kubo kubo_v0.33.0_linux-amd64.tar.gz

# Set repository location
ENV IPFS_PATH=/data/ipfs

# Create repository
RUN mkdir -p /data/ipfs

# Initialize repository
RUN ipfs init --profile=server

# Expose ports
EXPOSE 4001 5001 8080

# Start daemon
CMD ["ipfs", "daemon"]