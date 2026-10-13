FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y wget tar

# Download and install IPFS
RUN wget https://dist.ipfs.tech/kubo/v0.36.0/kubo_v0.36.0_linux-amd64.tar.gz && \
    tar -xzf kubo_v0.36.0_linux-amd64.tar.gz && \
    cd kubo && ./install.sh

# Initialize IPFS
RUN ipfs init

# Copy a local file
COPY sample.txt /sample.txt

# Generate the IPFS hash
CMD ["ipfs", "add", "/sample.txt"]