"""A small, educational in-memory implementation of the Raft consensus algorithm.

It covers leader election, heartbeats, log replication, and committing entries
after they are stored on a majority of nodes.  Network and disk persistence are
intentionally simplified for classroom demonstration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class LogEntry:
    term: int
    command: str


class RaftNode:
    """One server in an in-memory Raft cluster."""

    def __init__(self, node_id: int, cluster: "ClusterLike", election_timeout: int) -> None:
        self.node_id = node_id
        self.cluster = cluster
        self.election_timeout = election_timeout
        self.heartbeat_interval = 2
        self.current_term = 0
        self.voted_for: Optional[int] = None
        self.log: list[LogEntry] = []
        self.commit_index = -1
        self.last_applied = -1
        self.role = "follower"
        self.leader_id: Optional[int] = None
        self.last_heartbeat_tick = 0
        self.last_heartbeat_sent = 0
        self.votes_received: set[int] = set()
        self.next_index: dict[int, int] = {}
        self.match_index: dict[int, int] = {}
        self.state_machine: list[str] = []
        self.alive = True

    def tick(self, now: int) -> None:
        """Advance node timers by one logical clock tick."""
        if not self.alive:
            return
        if self.role == "leader":
            if now - self.last_heartbeat_sent >= self.heartbeat_interval:
                self.send_heartbeats(now)
            return
        if now - self.last_heartbeat_tick >= self.election_timeout:
            self.start_election(now)

    def start_election(self, now: int) -> None:
        self.role = "candidate"
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        self.leader_id = None
        self.last_heartbeat_tick = now
        print(f"Node {self.node_id} starts election for term {self.current_term}")

        last_index = len(self.log) - 1
        last_term = self.log[last_index].term if last_index >= 0 else 0
        for peer_id in self.cluster.peer_ids(self.node_id):
            response = self.cluster.request_vote(
                peer_id, self.current_term, self.node_id, last_index, last_term
            )
            if response is not None:
                self.receive_vote_response(peer_id, *response, now)

    def request_vote(
        self, term: int, candidate_id: int, last_log_index: int, last_log_term: int
    ) -> tuple[int, bool]:
        if term < self.current_term:
            return self.current_term, False
        if term > self.current_term:
            self.become_follower(term)

        own_last_index = len(self.log) - 1
        own_last_term = self.log[own_last_index].term if own_last_index >= 0 else 0
        candidate_is_up_to_date = (last_log_term, last_log_index) >= (own_last_term, own_last_index)
        grant = (self.voted_for in (None, candidate_id)) and candidate_is_up_to_date
        if grant:
            self.voted_for = candidate_id
        return self.current_term, grant

    def receive_vote_response(self, peer_id: int, term: int, granted: bool, now: int) -> None:
        if term > self.current_term:
            self.become_follower(term)
            return
        if self.role != "candidate" or term != self.current_term:
            return
        if granted:
            self.votes_received.add(peer_id)
            if len(self.votes_received) >= self.cluster.majority:
                self.become_leader(now)

    def become_leader(self, now: int) -> None:
        self.role = "leader"
        self.leader_id = self.node_id
        self.next_index = {peer: len(self.log) for peer in self.cluster.peer_ids(self.node_id)}
        self.match_index = {peer: -1 for peer in self.cluster.peer_ids(self.node_id)}
        print(f"Node {self.node_id} becomes LEADER for term {self.current_term}")
        self.send_heartbeats(now)

    def become_follower(self, new_term: int) -> None:
        self.role = "follower"
        self.current_term = new_term
        self.voted_for = None
        self.leader_id = None
        self.votes_received.clear()

    def send_heartbeats(self, now: int) -> None:
        self.last_heartbeat_sent = now
        for peer_id in self.cluster.peer_ids(self.node_id):
            self.replicate_to(peer_id, now)

    def replicate_to(self, peer_id: int, now: int) -> None:
        if self.role != "leader":
            return
        next_index = self.next_index[peer_id]
        prev_index = next_index - 1
        prev_term = self.log[prev_index].term if prev_index >= 0 else 0
        entries = self.log[next_index:]
        response = self.cluster.append_entries(
            peer_id, self.current_term, self.node_id, prev_index, prev_term, entries, self.commit_index, now
        )
        if response is None:
            return
        term, success, match_index = response
        if term > self.current_term:
            self.become_follower(term)
        elif success:
            self.match_index[peer_id] = match_index
            self.next_index[peer_id] = match_index + 1
            self.advance_commit_index()
        elif self.next_index[peer_id] > 0:
            self.next_index[peer_id] -= 1

    def append_entries(
        self, term: int, leader_id: int, prev_index: int, prev_term: int,
        entries: list[LogEntry], leader_commit: int, now: int,
    ) -> tuple[int, bool, int]:
        if term < self.current_term:
            return self.current_term, False, len(self.log) - 1
        if term > self.current_term or self.role != "follower":
            self.become_follower(term)
        self.leader_id = leader_id
        self.last_heartbeat_tick = now

        if prev_index >= len(self.log) or (prev_index >= 0 and self.log[prev_index].term != prev_term):
            return self.current_term, False, len(self.log) - 1
        insert_at = prev_index + 1
        for entry in entries:
            if insert_at < len(self.log) and self.log[insert_at].term != entry.term:
                self.log = self.log[:insert_at]
            if insert_at == len(self.log):
                self.log.append(entry)
            insert_at += 1
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log) - 1)
            self.apply_committed_entries()
        return self.current_term, True, len(self.log) - 1

    def submit(self, command: str, now: int) -> bool:
        """Accept a client command only when this node is the leader."""
        if not self.alive or self.role != "leader":
            return False
        self.log.append(LogEntry(self.current_term, command))
        print(f"Leader {self.node_id} accepts command: {command!r}")
        self.send_heartbeats(now)
        return True

    def advance_commit_index(self) -> None:
        for index in range(len(self.log) - 1, self.commit_index, -1):
            replicated = 1 + sum(match >= index for match in self.match_index.values())
            if replicated >= self.cluster.majority and self.log[index].term == self.current_term:
                self.commit_index = index
                self.apply_committed_entries()
                print(f"Leader {self.node_id} commits log entry {index}")
                return

    def apply_committed_entries(self) -> None:
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            self.state_machine.append(self.log[self.last_applied].command)


class ClusterLike:
    """Type-only interface supplied by cluster.Cluster."""

    majority: int

    def peer_ids(self, node_id: int) -> list[int]: ...
