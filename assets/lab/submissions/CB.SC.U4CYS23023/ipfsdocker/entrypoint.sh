#!/bin/sh
set -e

export IPFS_PATH=/data/ipfs

if [ ! -f "$IPFS_PATH/config" ]; then
    ipfs init
    ipfs config Addresses.API /ip4/0.0.0.0/tcp/5001
    ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080
fi

if [ -f "/data/sample_image.png" ]; then
    ipfs add --offline /data/sample_image.png
fi

exec ipfs daemon