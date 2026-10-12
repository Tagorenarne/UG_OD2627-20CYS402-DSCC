import threading
import random
import time
import heapq
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, List


class Role(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


@dataclass
class Entry:
    term: int
    payload: Any


@dataclass
class VoteReq:
    term: int
    cand: int
    last_idx: int
    last_term: int


@dataclass
class VoteResp:
    term: int
    granted: bool


@dataclass
class AppendReq:
    term: int
    leader: int
    prev_idx: int
    prev_term: int
    items: List[Entry]
    commit: int


@dataclass
class AppendResp:
    term: int
    ok: bool
    matched: int


class Fabric:
    def __init__(self, jitter=(0.004, 0.025)):
        self.members = {}
        self.loss = 0.0
        self.cut = set()
        self._pq = []
        self._ctr = 0
        self._jitter = jitter
        self._cv = threading.Condition()
        self.alive = True
        threading.Thread(target=self._pump, daemon=True).start()

    def attach(self, member):
        self.members[member.id] = member

    def dispatch(self, src, dst, msg):
        if random.random() < self.loss:
            return
        with self._cv:
            if src in self.cut or dst in self.cut:
                return
            when = time.time() + random.uniform(*self._jitter)
            heapq.heappush(self._pq, (when, self._ctr, src, dst, msg))
            self._ctr += 1
            self._cv.notify()

    def _pump(self):
        while self.alive:
            with self._cv:
                if not self._pq:
                    self._cv.wait(timeout=0.1)
                    continue
                when, _, src, dst, msg = self._pq[0]
                now = time.time()
                if when > now:
                    self._cv.wait(timeout=when - now)
                    continue
                heapq.heappop(self._pq)
                m = self.members.get(dst)
                if m and dst not in self.cut:
                    m.inbox.put((src, msg))

    def halt(self):
        self.alive = False
        with self._cv:
            self._cv.notify()


PULSE = 0.08
ELECTION_WINDOW = (0.25, 0.55)


class Replica:
    def __init__(self, rid: int, roster: List[int], fabric: Fabric):
        self.id = rid
        self.roster = list(roster)
        self.others = [i for i in roster if i != rid]
        self.fabric = fabric
        fabric.attach(self)

        self.term = 0
        self.ballot: Optional[int] = None
        self.wal: List[Entry] = [Entry(term=0, payload=None)]

        self.commit = 0
        self.applied = 0
        self.role = Role.FOLLOWER
        self.leader: Optional[int] = None

        self.follow_next = {}
        self.follow_match = {}

        self.tally = set()
        self.deadline = 0.0
        self.last_pulse = 0.0

        self.store = {}

        self.inbox = __import__("queue").Queue()
        self.mutex = threading.RLock()
        self.alive = False
        self._worker = None

    def launch(self):
        self.alive = True
        self._arm_timer()
        self._worker = threading.Thread(target=self._spin, daemon=True)
        self._worker.start()

    def halt(self):
        self.alive = False

    def _spin(self):
        while self.alive:
            now = time.time()
            with self.mutex:
                if self.role == Role.LEADER:
                    if now - self.last_pulse >= PULSE:
                        self._fan_out()
                        self.last_pulse = now
                elif now >= self.deadline:
                    self._campaign()
            try:
                src, msg = self.inbox.get(timeout=0.01)
            except Exception:
                continue
            self._route(src, msg)

    def _arm_timer(self):
        self.deadline = time.time() + random.uniform(*ELECTION_WINDOW)

    def _revert(self, term: int):
        self.term = term
        self.role = Role.FOLLOWER
        self.ballot = None
        self._arm_timer()

    def _campaign(self):
        self.role = Role.CANDIDATE
        self.term += 1
        self.ballot = self.id
        self.tally = {self.id}
        self._arm_timer()
        tail = len(self.wal) - 1
        tail_term = self.wal[tail].term
        for peer in self.others:
            self.fabric.dispatch(self.id, peer, VoteReq(
                term=self.term,
                cand=self.id,
                last_idx=tail,
                last_term=tail_term,
            ))

    def _ascend(self):
        self.role = Role.LEADER
        self.leader = self.id
        tail = len(self.wal) - 1
        self.follow_next = {p: tail + 1 for p in self.others}
        self.follow_match = {p: 0 for p in self.others}
        self.last_pulse = 0.0
        print(f"[replica {self.id}] ascended to LEADER, term {self.term}")

    def _route(self, src, msg):
        with self.mutex:
            if isinstance(msg, VoteReq):
                self._recv_vote_req(src, msg)
            elif isinstance(msg, VoteResp):
                self._recv_vote_resp(src, msg)
            elif isinstance(msg, AppendReq):
                self._recv_append_req(src, msg)
            elif isinstance(msg, AppendResp):
                self._recv_append_resp(src, msg)

    def _recv_vote_req(self, src, rv: VoteReq):
        if rv.term > self.term:
            self._revert(rv.term)
        granted = False
        if rv.term == self.term:
            tail = len(self.wal) - 1
            tail_term = self.wal[tail].term
            fresh = (rv.last_term > tail_term or
                     (rv.last_term == tail_term and rv.last_idx >= tail))
            if self.ballot in (None, rv.cand) and fresh:
                self.ballot = rv.cand
                granted = True
                self._arm_timer()
        self.fabric.dispatch(self.id, src, VoteResp(term=self.term, granted=granted))

    def _recv_vote_resp(self, src, resp: VoteResp):
        if resp.term > self.term:
            self._revert(resp.term)
            return
        if self.role != Role.CANDIDATE or resp.term != self.term:
            return
        if resp.granted:
            self.tally.add(src)
            if len(self.tally) > len(self.roster) // 2:
                self._ascend()

    def _recv_append_req(self, src, ar: AppendReq):
        if ar.term > self.term:
            self._revert(ar.term)
        ok = False
        matched = 0
        if ar.term == self.term:
            self.role = Role.FOLLOWER
            self.leader = ar.leader
            self._arm_timer()
            if (ar.prev_idx < len(self.wal) and
                    self.wal[ar.prev_idx].term == ar.prev_term):
                ok = True
                for i, e in enumerate(ar.items):
                    idx = ar.prev_idx + 1 + i
                    if idx < len(self.wal):
                        if self.wal[idx].term != e.term:
                            self.wal = self.wal[:idx]
                            self.wal.append(e)
                    else:
                        self.wal.append(e)
                matched = ar.prev_idx + len(ar.items)
                if ar.commit > self.commit:
                    self.commit = min(ar.commit, len(self.wal) - 1)
                    self._flush()
        self.fabric.dispatch(self.id, src, AppendResp(
            term=self.term, ok=ok, matched=matched))

    def _recv_append_resp(self, src, resp: AppendResp):
        if resp.term > self.term:
            self._revert(resp.term)
            return
        if self.role != Role.LEADER or resp.term != self.term:
            return
        if resp.ok:
            self.follow_match[src] = max(self.follow_match[src], resp.matched)
            self.follow_next[src] = self.follow_match[src] + 1
            self._bump_commit()
        else:
            self.follow_next[src] = max(1, self.follow_next[src] - 1)
            self._push(src)

    def _push(self, peer):
        nxt = self.follow_next[peer]
        prev = nxt - 1
        prev_term = self.wal[prev].term
        items = self.wal[nxt:]
        self.fabric.dispatch(self.id, peer, AppendReq(
            term=self.term,
            leader=self.id,
            prev_idx=prev,
            prev_term=prev_term,
            items=items,
            commit=self.commit,
        ))

    def _fan_out(self):
        for peer in self.others:
            self._push(peer)

    def _bump_commit(self):
        tail = len(self.wal) - 1
        for n in range(tail, self.commit, -1):
            if self.wal[n].term != self.term:
                continue
            votes = 1
            for p in self.others:
                if self.follow_match[p] >= n:
                    votes += 1
            if votes > len(self.roster) // 2:
                self.commit = n
                self._flush()
                break

    def _flush(self):
        while self.applied < self.commit:
            self.applied += 1
            self._exec(self.wal[self.applied].payload)

    def _exec(self, payload):
        if payload is None:
            return
        op = payload[0]
        if op == "put":
            _, k, v = payload
            self.store[k] = v
        elif op == "del":
            _, k = payload
            self.store.pop(k, None)

    def propose(self, payload):
        with self.mutex:
            if self.role != Role.LEADER:
                return False, self.leader
            self.wal.append(Entry(term=self.term, payload=payload))
            self._fan_out()
            return True, self.id


def current_leader(cluster):
    lead = [r for r in cluster if r.role == Role.LEADER]
    return max(lead, key=lambda r: r.term) if lead else None


def await_leader(cluster, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        l = current_leader(cluster)
        if l:
            return l
        time.sleep(0.05)
    return None


def propose_blocking(cluster, payload, timeout=3.0):
    start = time.time()
    while time.time() - start < timeout:
        l = current_leader(cluster)
        if l:
            ok, _ = l.propose(payload)
            if ok:
                return l
        time.sleep(0.05)
    return None


def main():
    random.seed(7)
    fabric = Fabric()
    ids = [10, 20, 30, 40, 50, 60, 70]
    cluster = [Replica(i, ids, fabric) for i in ids]
    for r in cluster:
        r.launch()

    print("=== Booting 7-replica cluster, awaiting a leader ===")
    lead = await_leader(cluster)
    print(f"Leader chosen: replica {lead.id} (term {lead.term})\n")

    print("=== Replicating a batch of writes ===")
    batch = [
        ("put", "alpha", 100),
        ("put", "beta", 200),
        ("put", "alpha", 111),
        ("del", "beta"),
    ]
    for payload in batch:
        propose_blocking(cluster, payload)
        print(f"proposed {payload}")
    time.sleep(0.5)

    print("\n=== Cutting off the current leader to trigger re-election ===")
    prior = current_leader(cluster)
    with fabric._cv:
        fabric.cut.add(prior.id)
    print(f"replica {prior.id} severed")

    successor = None
    start = time.time()
    while time.time() - start < 5.0:
        c = current_leader([r for r in cluster if r.id != prior.id])
        if c and c.id != prior.id:
            successor = c
            break
        time.sleep(0.05)
    print(f"Successor leader: replica {successor.id} (term {successor.term})")

    print("\n=== Committing under the successor ===")
    propose_blocking([r for r in cluster if r.id != prior.id], ("put", "gamma", 999))
    time.sleep(0.5)

    print("\n=== Rejoining the severed replica ===")
    with fabric._cv:
        fabric.cut.discard(prior.id)
    time.sleep(1.0)

    print("\n=== Final cluster snapshot ===")
    for r in sorted(cluster, key=lambda x: x.id):
        terms = [e.term for e in r.wal]
        print(f"replica {r.id}: role={r.role.value:9s} term={r.term} "
              f"commit={r.commit} store={r.store} wal={terms}")

    floor = min(r.commit for r in cluster if r.id not in fabric.cut)
    ref = cluster[0].wal
    ok = all(
        [e.term for e in r.wal[:floor + 1]] == [e.term for e in ref[:floor + 1]]
        for r in cluster
    )
    print(f"\nCommitted prefixes agree across replicas: {ok}")

    for r in cluster:
        r.halt()
    fabric.halt()


if __name__ == "__main__":
    main()