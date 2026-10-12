from dataclasses import dataclass
from typing import Dict, List, Optional, Set


# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------
@dataclass
class Message:
    """Message passed between processes."""
    msg_id: str
    sender: str
    receiver: str
    timestamp: int  # Lamport timestamp attached by the sender


@dataclass
class Event:
    """One recorded event in a process."""
    event_id: str       # E1, E2, ...
    process: str        # P1, P2, ...
    etype: str          # LOCAL / SEND / RECEIVE
    timestamp: int      # Lamport timestamp of the event
    msg_id: Optional[str] = None  # message involved (SEND / RECEIVE)


# --------------------------------------------------------------------------
# Process
# --------------------------------------------------------------------------
class Process:
    """A simulated distributed process with its own logical clock."""

    def __init__(self, name: str, system: "DistributedSystem"):
        self.name = name
        self.clock = 0
        self.system = system
        self.events: List[Event] = []
        self.inbox: List[Message] = []

    # Rule 1: local event
    def local_event(self) -> Event:
        self.clock += 1
        return self._record("LOCAL", self.clock)

    # Rule 2: send event
    def send_message(self, receiver: "Process") -> Message:
        self.clock += 1
        msg = Message(
            msg_id=self.system.next_msg_id(),
            sender=self.name,
            receiver=receiver.name,
            timestamp=self.clock,       # timestamp travels with the message
        )
        self._record("SEND", self.clock, msg.msg_id)
        receiver.inbox.append(msg)      # deliver to destination
        return msg

    # Rule 3: receive event
    def receive_message(self, msg: Message) -> Event:
        if msg not in self.inbox:
            raise ValueError(f"{self.name} has no pending message {msg.msg_id}")
        self.inbox.remove(msg)
        self.clock = max(self.clock, msg.timestamp) + 1
        return self._record("RECEIVE", self.clock, msg.msg_id)

    def _record(self, etype: str, ts: int, msg_id: Optional[str] = None) -> Event:
        ev = Event(self.system.next_event_id(), self.name, etype, ts, msg_id)
        self.events.append(ev)
        self.system.log_event(ev)
        return ev


# --------------------------------------------------------------------------
# Distributed system (holds processes, global log, causal graph)
# --------------------------------------------------------------------------
class DistributedSystem:
    def __init__(self, names: List[str], title: str = "LAMPORT LOGICAL CLOCK"):
        self.title = title
        self.processes: Dict[str, Process] = {n: Process(n, self) for n in names}
        self.log: List[Event] = []
        self._event_count = 0
        self._msg_count = 0
        # True causal edges (event_id -> set of event_ids that directly follow it).
        # Used ONLY to verify concurrency; the clocks themselves never see this.
        self._edges: Dict[str, Set[str]] = {}
        self._send_event_of_msg: Dict[str, str] = {}

    # ---- id generators ----
    def next_event_id(self) -> str:
        self._event_count += 1
        return f"E{self._event_count}"

    def next_msg_id(self) -> str:
        self._msg_count += 1
        return f"M{self._msg_count}"

    # ---- logging + causal graph ----
    def log_event(self, ev: Event) -> None:
        proc = self.processes[ev.process]
        self._edges.setdefault(ev.event_id, set())
        # program-order edge: previous event in same process -> this event
        if len(proc.events) >= 2:
            prev = proc.events[-2]  # current event is already appended
            self._edges[prev.event_id].add(ev.event_id)
        if ev.etype == "SEND":
            self._send_event_of_msg[ev.msg_id] = ev.event_id
        elif ev.etype == "RECEIVE":
            self._edges[self._send_event_of_msg[ev.msg_id]].add(ev.event_id)
        self.log.append(ev)
        self._print_live(ev)

    def _print_live(self, ev: Event) -> None:
        extra = f"  ({ev.msg_id})" if ev.msg_id else ""
        print(f"  {ev.process}  {ev.event_id:<4} {ev.etype:<8} "
              f"-> clock = {ev.timestamp}{extra}")

    # ---- helpers ----
    def get(self, name: str) -> Process:
        return self.processes[name]

    def happened_before(self, a: Event, b: Event) -> bool:
        """True if a -> b (path in the causal graph)."""
        stack, seen = [a.event_id], set()
        while stack:
            cur = stack.pop()
            if cur == b.event_id:
                return True
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(self._edges.get(cur, ()))
        return False

    def concurrent(self, a: Event, b: Event) -> bool:
        return (a.event_id != b.event_id
                and not self.happened_before(a, b)
                and not self.happened_before(b, a))

    def print_event_table(self) -> None:
        print("\n" + "=" * 52)
        print(f"{self.title:^52}")
        print("=" * 52)
        print(f"\n{'Process':<10} {'Event':<8} {'Type':<10} {'Timestamp':>9}")
        print("-" * 52)
        for ev in self.log:
            print(f"{ev.process:<10} {ev.event_id:<8} {ev.etype:<10} {ev.timestamp:>9}")
        print("-" * 52)


# --------------------------------------------------------------------------
# Part D: exercise scenario
# --------------------------------------------------------------------------
def run_scenario() -> DistributedSystem:
    print("\n>>> Running exercise scenario (live trace)\n")
    ds = DistributedSystem(["P1", "P2", "P3"])
    p1, p2, p3 = ds.get("P1"), ds.get("P2"), ds.get("P3")

    p1.local_event()                 # 1. P1 local
    m1 = p1.send_message(p2)         # 2. P1 -> P2
    p2.receive_message(m1)           # 3. P2 receives from P1
    p2.local_event()                 # 4. P2 local
    m2 = p2.send_message(p3)         # 5. P2 -> P3
    p1.local_event()                 # 6. P1 local
    m3 = p1.send_message(p3)         # 7. P1 -> P3
    p3.receive_message(m2)           # 8. P3 receives from P2
    p3.receive_message(m3)           # 9. P3 receives from P1

    ds.print_event_table()
    return ds


# --------------------------------------------------------------------------
# Part H: causal ordering
# --------------------------------------------------------------------------
def demo_causal_ordering(ds: DistributedSystem) -> None:
    print("\n" + "=" * 52)
    print("CAUSAL ORDERING   (a -> b  implies  L(a) < L(b))")
    print("=" * 52)

    def find(etype: str, msg_id: str) -> Event:
        return next(e for e in ds.log if e.etype == etype and e.msg_id == msg_id)

    pairs = [("M1", "P1 SEND M1", "P2 RECEIVE M1"),
             ("M2", "P2 SEND M2", "P3 RECEIVE M2"),
             ("M3", "P1 SEND M3", "P3 RECEIVE M3")]

    print(f"\n{'Event A':<14} {'Event B':<16} {'TS A':>5} {'TS B':>5}  L(A)<L(B)?")
    print("-" * 52)
    for mid, a_label, b_label in pairs:
        a, b = find("SEND", mid), find("RECEIVE", mid)
        assert ds.happened_before(a, b)
        print(f"{a_label:<14} {b_label:<16} {a.timestamp:>5} {b.timestamp:>5}  "
              f"{a.timestamp < b.timestamp}")
    print("-" * 52)


# --------------------------------------------------------------------------
# Part I: concurrent events
# --------------------------------------------------------------------------
def demo_concurrent_events() -> None:
    print("\n" + "=" * 52)
    print("CONCURRENT EVENTS")
    print("=" * 52)
    print("\nTwo processes that never communicate:\n")

    ds = DistributedSystem(["P1", "P2"], title="NO COMMUNICATION")
    p1, p2 = ds.get("P1"), ds.get("P2")
    e1 = p1.local_event()
    e2 = p1.local_event()
    e3 = p2.local_event()
    e4 = p2.local_event()

    print(f"\n{'Pair':<10} {'TS A':>5} {'TS B':>5}  {'Concurrent?':<12} {'Same TS?'}")
    print("-" * 52)
    for a, b in [(e1, e3), (e1, e4), (e2, e3), (e2, e4), (e1, e2)]:
        print(f"{a.event_id}-{b.event_id:<7} {a.timestamp:>5} {b.timestamp:>5}  "
              f"{str(ds.concurrent(a, b)):<12} {a.timestamp == b.timestamp}")
    print("-" * 52)
    print("E1 and E3 are concurrent AND share timestamp 1 -> different events "
          "can have the same Lamport timestamp.")


def demo_converse_fails(ds: DistributedSystem) -> None:
    """Show that L(a) < L(b) does NOT imply a -> b."""
    print("\n" + "=" * 52)
    print("LIMITATION: L(a) < L(b) does NOT imply a -> b")
    print("=" * 52)
    # P1's second local event vs P2's local event in the main scenario
    local_p1 = [e for e in ds.log if e.process == "P1" and e.etype == "LOCAL"][1]
    local_p2 = [e for e in ds.log if e.process == "P2" and e.etype == "LOCAL"][0]
    print(f"\n{local_p1.process} {local_p1.event_id}: L = {local_p1.timestamp}")
    print(f"{local_p2.process} {local_p2.event_id}: L = {local_p2.timestamp}")
    print(f"L({local_p1.event_id}) < L({local_p2.event_id})        : "
          f"{local_p1.timestamp < local_p2.timestamp}")
    print(f"{local_p1.event_id} happened-before {local_p2.event_id}   : "
          f"{ds.happened_before(local_p1, local_p2)}")
    print(f"Actually concurrent          : {ds.concurrent(local_p1, local_p2)}")
    print("\n=> Timestamps alone cannot tell us if two events are concurrent.")
    print("   (Vector clocks can.)")


# --------------------------------------------------------------------------
if __name__ == "__main__":
    system = run_scenario()
    demo_causal_ordering(system)
    demo_concurrent_events()
    demo_converse_fails(system)