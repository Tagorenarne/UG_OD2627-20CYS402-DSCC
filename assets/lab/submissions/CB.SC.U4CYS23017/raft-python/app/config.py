import os

NODE_ID = os.getenv("NODE_ID", "node1")
PORT = int(os.getenv("PORT", 5001))

PEERS = {
    "node1": "http://node1:5001",
    "node2": "http://node2:5002",
    "node3": "http://node3:5003"
}

OTHER_PEERS = {
    node: url
    for node, url in PEERS.items()
    if node != NODE_ID
}
