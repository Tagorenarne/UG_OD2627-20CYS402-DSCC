# Use Ubuntu as the base image
FROM ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install wget and tar
RUN apt-get update && \
    apt-get install -y wget tar && \
    rm -rf /var/lib/apt/lists/*

# Download IPFS
RUN wget https://dist.ipfs.tech/kubo/v0.30.0/kubo_v0.30.0_linux-amd64.tar.gz && \
    tar -xvzf kubo_v0.30.0_linux-amd64.tar.gz && \
    cd kubo && \
    bash install.sh

# Initialize IPFS
RUN ipfs init

# Working directory
WORKDIR /data

# Copy sample file
COPY sample.txt .

# Add file to IPFS and print its hash
CMD sh -c "echo 'Uploading sample.txt to IPFS...'; ipfs add sample.txt"