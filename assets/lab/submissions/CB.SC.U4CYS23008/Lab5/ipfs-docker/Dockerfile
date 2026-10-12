# ---- Base image: lightweight Linux ----
FROM ubuntu:22.04

# ---- Install dependencies needed to fetch and run IPFS ----
RUN apt-get update && \
    apt-get install -y wget tar && \
    rm -rf /var/lib/apt/lists/*

# ---- Set working directory ----
WORKDIR /app

# ---- Download and install IPFS (Kubo) binary ----
RUN wget https://dist.ipfs.tech/kubo/v0.29.0/kubo_v0.29.0_linux-amd64.tar.gz && \
    tar -xvzf kubo_v0.29.0_linux-amd64.tar.gz && \
    cd kubo && \
    bash install.sh && \
    cd .. && \
    rm -rf kubo kubo_v0.29.0_linux-amd64.tar.gz

# ---- Copy sample file to be uploaded ----
COPY sample.txt /app/sample.txt

# ---- Copy the entrypoint script ----
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# ---- Expose IPFS default ports (API, Gateway, Swarm) ----
EXPOSE 4001 5001 8080

# ---- Run the entrypoint script on container start ----
ENTRYPOINT ["/app/entrypoint.sh"]