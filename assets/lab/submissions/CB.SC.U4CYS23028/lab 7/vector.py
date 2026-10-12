from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

Vector = Tuple[int, ...]

BEFORE = "V1 happened before V2"
AFTER = "V2 happened before V1"
CONCURRENT = "V1 and V2 are concurrent"
SAME = "V1 and V2 represent the same timestamp"

def fmt(v) -> str:
    """Format a vector as [a,b,c]."""
    return "[" + ",".join(str(x) for x in v) + "]"


# --------------------------------------------------------------------------
# Vector comparison (Part J)
# --------------------------------------------------------------------------
def compare_vectors(v1, v2) -> str:
    """Compare two vector timestamps."""
    le = all(a <= b for a, b in zip(v1, v2))   # V1 <= V2
    ge = all(a >= b for a, b in zip(v1, v2))   # V2 <= V1
    if le and ge:
        return SAME
    if le:
        return BEFORE
    if ge:
        return AFTER
    return CONCURRENT


def relation_symbol(v1, v2, name1: str = "A", name2: str = "B") -> str:
    """Return A -> B, B -> A, A || B (or A == B)."""
    result = compare_vectors(v1, v2)
    if result == BEFORE:
        return f"{name1} -> {name2}"
    if result == AFTER:
        return f"{name2} -> {name1}"
    if result == CONCURRENT:
        return f"{name1} || {name2}"
    return f"{name1} == {name2}"


# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------
@dataclass
class Message:
    """Message passed between processes."""
    msg_id: str
    sender: str
    receiver: str
    vector: Vector  # vector timestamp attached by the sender


@dataclass
class Event:
    """One recorded event in a process."""
    event_id: str                  # E1, E2, ...
    process: str                   # P1, P2, ...
    etype: str                     # LOCAL / SEND / RECEIVE
    vector: Vector                 # vector timestamp of the event
    msg_id: Optional[str] = None   # message involved (SEND / RECEIVE)
    peer: Optional[str] = None     # other process involved (SEND / RECEIVE)


# --------------------------------------------------------------------------
# Process
# --------------------------------------------------------------------------
class Process:
    """A simulated distributed process with its own vector clock."""

    def __init__(self, name: str, index: int, system: "DistributedSystem"):
        self.name = name
        self.index = index                       # position in the vector
        self.system = system
        self.clock: List[int] = [0] * system.n   # vector clock
        self.events: List[Event] = []
        self.inbox: List[Message] = []

    # Rule 1: local event
    def local_event(self) -> Event:
        self.clock[self.index] += 1
        return self._record("LOCAL")

    # Rule 2: send event
    def send_message(self, receiver: "Process") -> Message:
        self.clock[self.index] += 1
        msg = Message(
            msg_id=self.system.next_msg_id(),
            sender=self.name,
            receiver=receiver.name,
            vector=tuple(self.clock),        # vector travels with the message
        )
        self._record("SEND", msg.msg_id, receiver.name)
        receiver.inbox.append(msg)           # deliver to destination
        return msg

    # Rule 3: receive event
    def receive_message(self, msg: Message) -> Event:
        if msg not in self.inbox:
            raise ValueError(f"{self.name} has no pending message {msg.msg_id}")
        self.inbox.remove(msg)
        # component-wise maximum
        self.clock = [max(a, b) for a, b in zip(self.clock, msg.vector)]
        # then increment own component
        self.clock[self.index] += 1
        return self._record("RECEIVE", msg.msg_id, msg.sender)

    def _record(self, etype: str, msg_id: Optional[str] = None,
                peer: Optional[str] = None) -> Event:
        ev = Event(self.system.next_event_id(), self.name, etype,
                   tuple(self.clock), msg_id, peer)
        self.events.append(ev)
        self.system.log.append(ev)
        self.system.print_live(ev)
        return ev


# --------------------------------------------------------------------------
# Distributed system
# --------------------------------------------------------------------------
class DistributedSystem:
    def __init__(self, names: List[str], title: str = "VECTOR CLOCK"):
        self.title = title
        self.n = len(names)
        self.processes: Dict[str, Process] = {
            name: Process(name, i, self) for i, name in enumerate(names)
        }
        self.log: List[Event] = []
        self._event_count = 0
        self._msg_count = 0

    def next_event_id(self) -> str:
        self._event_count += 1
        return f"E{self._event_count}"

    def next_msg_id(self) -> str:
        self._msg_count += 1
        return f"M{self._msg_count}"

    def get(self, name: str) -> Process:
        return self.processes[name]

    def event(self, event_id: str) -> Event:
        return next(e for e in self.log if e.event_id == event_id)

    def print_live(self, ev: Event) -> None:
        extra = f"  ({ev.msg_id})" if ev.msg_id else ""
        print(f"  {ev.process}  {ev.event_id:<4} {ev.etype:<8} "
              f"-> {fmt(ev.vector)}{extra}")

    def print_event_log(self) -> None:
        print("\n" + "=" * 56)
        print(f"{self.title:^56}")
        print("=" * 56)
        print(f"\n{'Process':<10} {'Event':<8} {'Type':<11} Vector Timestamp")
        print("-" * 56)
        for ev in self.log:
            print(f"{ev.process:<10} {ev.event_id:<8} {ev.etype:<11} {fmt(ev.vector)}")
        print("-" * 56)

    def print_results_table(self) -> None:
        print("\n" + "=" * 56)
        print("RESULTS TABLE")
        print("=" * 56)
        print(f"\n{'Event':<7}{'Process':<9}{'Type':<10}{'Message':<10}Vector Timestamp")
        print("-" * 56)
        for ev in self.log:
            if ev.etype == "SEND":
                msg = f"{ev.process}->{ev.peer}"
            elif ev.etype == "RECEIVE":
                msg = f"{ev.peer}->{ev.process}"
            else:
                msg = "-"
            print(f"{ev.event_id:<7}{ev.process:<9}{ev.etype:<10}{msg:<10}{fmt(ev.vector)}")
        print("-" * 56)


# --------------------------------------------------------------------------
# Part E: exercise scenario
# --------------------------------------------------------------------------
def run_scenario() -> DistributedSystem:
    print("\n>>> Running exercise scenario (live trace)\n")
    ds = DistributedSystem(["P1", "P2", "P3"])
    p1, p2, p3 = ds.get("P1"), ds.get("P2"), ds.get("P3")

    p1.local_event()                 # 1. E1: P1 local
    m1 = p1.send_message(p2)         # 2. E2: P1 -> P2 (M1)
    p2.receive_message(m1)           # 3. E3: P2 receives M1
    p2.local_event()                 # 4. E4: P2 local
    m2 = p2.send_message(p3)         # 5. E5: P2 -> P3 (M2)
    p1.local_event()                 # 6. E6: P1 local
    m3 = p1.send_message(p3)         # 7. E7: P1 -> P3 (M3)
    p3.receive_message(m2)           # 8. E8: P3 receives M2
    p3.receive_message(m3)           # 9. E9: P3 receives M3

    ds.print_event_log()
    ds.print_results_table()
    return ds


# --------------------------------------------------------------------------
# Part M: required experiment (4 cases)
# --------------------------------------------------------------------------
def demo_cases(ds: DistributedSystem) -> None:
    print("\n" + "=" * 56)
    print("REQUIRED EXPERIMENT")
    print("=" * 56)

    def show(label: str, a: str, b: str) -> None:
        ea, eb = ds.event(a), ds.event(b)
        print(f"  {label:<22} {a} {fmt(ea.vector)}  vs  {b} {fmt(eb.vector)}"
              f"  =>  {relation_symbol(ea.vector, eb.vector, a, b)}")

    print("\nCase 1 - Same process ordering (P1 E1 -> P1 E2)")
    show("VC(E1) < VC(E2)", "E1", "E2")

    print("\nCase 2 - Message-based causality (P1 SEND -> P2 RECEIVE)")
    show("VC(SEND) < VC(RECV)", "E2", "E3")

    print("\nCase 3 - Transitive causality (P1 -> P2 -> P3)")
    show("E2 (P1 send) vs E5", "E2", "E5")
    show("E5 (P2 send) vs E8", "E5", "E8")
    show("E2 (P1 send) vs E8", "E2", "E8")
    print("  P1's knowledge (first component = 2) reaches P3 via P2: M2 carries")
    print("  [2,3,0], so E8 = [2,3,1] already reflects P1's events E1 and E2,")
    print("  even though the message that delivered it came from P2, not P1.")

    print("\nCase 4 - Concurrent events")
    show("E6 vs E4", "E6", "E4")
    a, b = ds.event("E6").vector, ds.event("E4").vector
    print(f"  VC(E6) <= VC(E4)? {all(x <= y for x, y in zip(a, b))}")
    print(f"  VC(E4) <= VC(E6)? {all(x <= y for x, y in zip(b, a))}")
    print("  Neither is <= the other  =>  E6 || E4")


# --------------------------------------------------------------------------
# Part O: causal relationship table
# --------------------------------------------------------------------------
def causal_table(ds: DistributedSystem) -> None:
    print("\n" + "=" * 56)
    print("CAUSAL RELATIONSHIP TABLE")
    print("=" * 56)
    pairs = [("E1", "E2"), ("E2", "E3"), ("E5", "E8"), ("E6", "E4"), ("E7", "E5")]
    print(f"\n{'A':<5}{'B':<5}{'Vector A':<12}{'Vector B':<12}Relationship")
    print("-" * 56)
    for a, b in pairs:
        ea, eb = ds.event(a), ds.event(b)
        print(f"{a:<5}{b:<5}{fmt(ea.vector):<12}{fmt(eb.vector):<12}"
              f"{relation_symbol(ea.vector, eb.vector, a, b)}")
    print("-" * 56)


# --------------------------------------------------------------------------
# compare_vectors() demonstration
# --------------------------------------------------------------------------
def demo_compare() -> None:
    print("\n" + "=" * 56)
    print("compare_vectors() EXAMPLES")
    print("=" * 56)
    tests = [
        ((2, 3, 1), (4, 3, 2)),
        ((4, 3, 2), (2, 3, 1)),
        ((3, 0, 0), (2, 2, 0)),
        ((1, 2, 3), (1, 2, 3)),
    ]
    print()
    for v1, v2 in tests:
        print(f"  {fmt(v1)} vs {fmt(v2)} : {compare_vectors(v1, v2)}")


# --------------------------------------------------------------------------
# Lamport vs Vector (why vector clocks detect concurrency)
# --------------------------------------------------------------------------
def demo_vs_lamport(ds: DistributedSystem) -> None:
    print("\n" + "=" * 56)
    print("LAMPORT vs VECTOR on the same events (E6 vs E4)")
    print("=" * 56)
    print("\n  Lamport timestamps from Lab 7A: E6 = 3, E4 = 4  ->  3 < 4")
    print("  (looks ordered, but Lamport cannot tell it's concurrent)")
    e6, e4 = ds.event("E6"), ds.event("E4")
    print(f"  Vector timestamps:              E6 = {fmt(e6.vector)}, "
          f"E4 = {fmt(e4.vector)}")
    print(f"  -> {relation_symbol(e6.vector, e4.vector, 'E6', 'E4')}  "
          f"(correctly detected as concurrent)")


# --------------------------------------------------------------------------
if __name__ == "__main__":
    system = run_scenario()
    demo_cases(system)
    causal_table(system)
    demo_compare()
    demo_vs_lamport(system)