# Step 1: Use Alpine Linux as the base image (lightweight)
FROM alpine:latest

# Step 2: Install dependencies needed to download and extract IPFS
RUN apk add --no-cache wget tar bash libc6-compat

# Step 3: Download and install IPFS (Kubo) binary
RUN wget https://dist.ipfs.tech/kubo/v0.29.0/kubo_v0.29.0_linux-amd64.tar.gz -O /tmp/kubo.tar.gz \
    && tar -xzf /tmp/kubo.tar.gz -C /tmp \
    && mv /tmp/kubo/ipfs /usr/local/bin/ipfs \
    && rm -rf /tmp/kubo /tmp/kubo.tar.gz \
    && ipfs --version

# Step 4: Set the working directory inside the container
WORKDIR /app

# Step 5: Copy the file to be uploaded to IPFS
COPY hi.txt .

# Step 6: Copy the upload script into the container
COPY upload_to_ipfs.sh .

# Step 7: Make the script executable
RUN chmod +x upload_to_ipfs.sh

# Step 8: Run the upload script when the container starts
CMD ["sh", "/app/upload_to_ipfs.sh"]
