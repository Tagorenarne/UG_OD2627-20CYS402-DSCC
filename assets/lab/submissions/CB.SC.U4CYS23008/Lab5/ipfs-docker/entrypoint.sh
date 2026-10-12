#!/bin/sh
set -e

echo "Initializing IPFS repository..."
ipfs init

echo "Starting IPFS daemon in background..."
ipfs daemon --init &

# Wait for the daemon to be fully up
sleep 5

echo "Uploading sample.txt to IPFS..."
HASH=$(ipfs add -q /app/sample.txt)

echo "=========================================="
echo "File uploaded successfully!"
echo "IPFS Hash (CID): $HASH"
echo "=========================================="

# Keep the container running so daemon stays alive
wait