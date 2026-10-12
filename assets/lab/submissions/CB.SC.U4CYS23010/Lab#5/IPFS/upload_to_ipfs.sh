#!/bin/sh

echo "========================================"
echo "  IPFS File Upload Script"
echo "========================================"

echo ""
echo "Step 1: Initializing IPFS repository..."
ipfs init

echo ""
echo "Step 2: Adding file to IPFS..."
echo ""
echo "File contents:"
cat /app/hi.txt
echo ""

RESULT=$(ipfs add -q /app/hi.txt)

echo ""
echo "========================================"
echo "  FILE SUCCESSFULLY ADDED TO IPFS!"
echo "========================================"
echo ""
echo "  IPFS Hash: $RESULT"
echo ""
echo "========================================"
