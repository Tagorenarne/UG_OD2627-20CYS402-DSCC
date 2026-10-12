"""In-memory transport used by the educational Raft implementation."""

from __future__ import annotations

from raft import LogEntry, RaftNode


class Cluster:
    def __init__(self, node_count: int = 3) -> None:
        self.time = 0
        self.nodes = {
            node_id: RaftNode(node_id, self, election_timeout=5 + node_id * 2)
            for node_id in range(node_count)
        }
        self.majority = node_count // 2 + 1

    def peer_ids(self, node_id: int) -> list[int]:
        return [peer for peer in self.nodes if peer != node_id]

    def request_vote(self, target: int, term: int, candidate: int, last_index: int, last_term: int):
        node = self.nodes[target]
        if not node.alive:
            return None
        return node.request_vote(term, candidate, last_index, last_term)

    def append_entries(
        self, target: int, term: int, leader: int, prev_index: int, prev_term: int,
        entries: list[LogEntry], leader_commit: int, now: int,
    ):
        node = self.nodes[target]
        if not node.alive:
            return None
        return node.append_entries(term, leader, prev_index, prev_term, entries, leader_commit, now)

    def tick(self, times: int = 1) -> None:
        for _ in range(times):
            self.time += 1
            for node in self.nodes.values():
                node.tick(self.time)

    def leader(self):
        return next((node for node in self.nodes.values() if node.alive and node.role == "leader"), None)

    def stop(self, node_id: int) -> None:
        self.nodes[node_id].alive = False
        print(f"Node {node_id} stopped (simulated failure)")
