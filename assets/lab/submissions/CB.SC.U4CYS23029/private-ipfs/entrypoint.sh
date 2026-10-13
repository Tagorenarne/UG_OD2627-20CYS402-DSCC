#!/bin/bash

set -e

echo "Initializing IPFS..."

ipfs init

echo "Installing swarm key..."
cp /tmp/swarm.key ~/.ipfs/swarm.key

echo "Removing public bootstrap nodes..."
ipfs bootstrap rm --all

echo "Starting IPFS daemon..."
ipfs daemon &
PID=$!

echo "Waiting for daemon..."
sleep 8

echo "Uploading sample file..."
CID=$(ipfs add -Q /sample.txt)

echo ""
echo "====================================="
echo "File uploaded successfully"
echo "CID (Hash): $CID"
echo "====================================="

wait $PID