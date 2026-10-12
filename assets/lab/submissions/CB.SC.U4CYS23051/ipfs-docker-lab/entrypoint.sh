#!/bin/sh
set -e

# Initialize the IPFS repo only if it hasn't been initialized yet
if [ ! -d "$IPFS_PATH" ] || [ -z "$(ls -A "$IPFS_PATH" 2>/dev/null)" ]; then
    echo "Initializing IPFS repository..."
    ipfs init
fi

# Start the IPFS daemon in the background (offline mode: no need to
# connect to the public swarm just to add/hash a local file)
echo "Starting IPFS daemon..."
ipfs daemon --offline &
DAEMON_PID=$!

# Give the daemon a few seconds to come up before we talk to it
sleep 5

echo ""
echo "Uploading sample.txt to IPFS..."
HASH=$(ipfs add -q /data/sample.txt)

echo ""
echo "=========================================="
echo " File uploaded successfully!"
echo " IPFS Hash (CID): $HASH"
echo "=========================================="
echo ""

# Stop the daemon cleanly and exit
kill "$DAEMON_PID"
wait "$DAEMON_PID" 2>/dev/null
