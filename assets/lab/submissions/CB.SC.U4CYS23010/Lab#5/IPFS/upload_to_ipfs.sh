#!/bin/sh

echo "========================================"
echo "  IPFS File Upload Script"
echo "========================================"

# Step 1: Initialize the IPFS repository
echo ""
echo "Step 1: Initializing IPFS repository..."
ipfs init

# Step 2: Add the file to IPFS (this works offline, no daemon needed)
echo ""
echo "Step 2: Adding file to IPFS..."
echo ""
echo "File contents:"
cat /app/hi.txt
echo ""

# Step 3: Upload the file and capture the hash
RESULT=$(ipfs add -q /app/hi.txt)

echo ""
echo "========================================"
echo "  FILE SUCCESSFULLY ADDED TO IPFS!"
echo "========================================"
echo ""
echo "  IPFS Hash: $RESULT"
echo ""
echo "========================================"
