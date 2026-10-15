"""
20CYS402 - Distributed Systems and Cloud Computing
Lab #8B - Vector Clock

Simulates P1, P2, and P3, dynamically computes vector timestamps,
checks causal ordering, and detects concurrent events.
No third-party packages or Docker required.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

Vector = List[int]


@dataclass
class Message:
    message_id: str
    sender: str
    receiver: str
    timestamp: Vector


@dataclass
class Event:
    process: str
    event_id: str
    event_type: str
    timestamp: Vector
    message: str = "-"


class Process:
    def __init__(self, name: str, process_index: int, process_count: int,
                 event_log: List[Event]):
        self.name = name
        self.index = process_index
        self.clock: Vector = [0] * process_count
        self.event_log = event_log

    def local_event(self, event_id: str) -> Vector:
        self.clock[self.index] += 1
        timestamp = self.clock.copy()
        self.event_log.append(Event(self.name, event_id, "LOCAL", timestamp))
        return timestamp

    def send_message(self, receiver: "Process", message_id: str) -> Message:
        self.clock[self.index] += 1
        timestamp = self.clock.copy()
        message = Message(message_id, self.name, receiver.name, timestamp)
        self.event_log.append(
            Event(self.name, message_id, "SEND", timestamp,
                  f"{self.name} -> {receiver.name}")
        )
        return message

    def receive_message(self, message: Message, event_id: str) -> Vector:
        if message.receiver != self.name:
            raise ValueError(
                f"Message {message.message_id} is addressed to {message.receiver}, "
                f"not {self.name}"
            )
        if len(message.timestamp) != len(self.clock):
            raise ValueError("Message vector length does not match process count.")

        self.clock = [
            max(local_value, received_value)
            for local_value, received_value in zip(self.clock, message.timestamp)
        ]
        self.clock[self.index] += 1
        timestamp = self.clock.copy()
        self.event_log.append(
            Event(self.name, event_id, "RECEIVE", timestamp,
                  f"{message.sender} -> {message.receiver}")
        )
        return timestamp


def vector_leq(a: Vector, b: Vector) -> bool:
    """Return True if every component of a is <= the corresponding component of b."""
    return len(a) == len(b) and all(x <= y for x, y in zip(a, b))


def compare_vectors(a: Vector, b: Vector) -> str:
    """Classify vector timestamps using the happened-before relation."""
    if a == b:
        return "SAME TIMESTAMP"
    if vector_leq(a, b):
        return "A -> B (A happened before B)"
    if vector_leq(b, a):
        return "B -> A (B happened before A)"
    return "A || B (CONCURRENT)"


def fmt(vector: Vector) -> str:
    return "[" + ",".join(str(x) for x in vector) + "]"


def print_event_log(events: List[Event]) -> None:
    print("=" * 88)
    print("                              VECTOR CLOCK")
    print("=" * 88)
    print(f"{'Process':<10}{'Event':<10}{'Type':<12}{'Vector Timestamp':<20}Message")
    print("-" * 88)
    for event in events:
        print(
            f"{event.process:<10}{event.event_id:<10}{event.event_type:<12}"
            f"{fmt(event.timestamp):<20}{event.message}"
        )
    print("-" * 88)


def main() -> None:
    events: List[Event] = []
    processes: Dict[str, Process] = {
        "P1": Process("P1", 0, 3, events),
        "P2": Process("P2", 1, 3, events),
        "P3": Process("P3", 2, 3, events),
    }
    p1, p2, p3 = processes["P1"], processes["P2"], processes["P3"]

    # Required sequence. All timestamps are calculated by the algorithm.
    t_e1 = p1.local_event("E1")
    m1 = p1.send_message(p2, "M1")             # E2
    t_e3 = p2.receive_message(m1, "E3")
    t_e4 = p2.local_event("E4")
    m2 = p2.send_message(p3, "M2")             # E5
    t_e6 = p1.local_event("E6")
    m3 = p1.send_message(p3, "M3")             # E7
    t_e8 = p3.receive_message(m2, "E8")
    t_e9 = p3.receive_message(m3, "E9")

    print_event_log(events)

    # Event lookup uses the event log, not hard-coded timestamps.
    by_event: Dict[str, Event] = {e.event_id: e for e in events}
    # The SEND rows are labelled by message ID in the event log; add exercise-event aliases.
    by_event["E2"] = by_event["M1"]
    by_event["E5"] = by_event["M2"]
    by_event["E7"] = by_event["M3"]

    print("\nVECTOR COMPARISON / CAUSAL RELATIONSHIPS")
    print("-" * 88)
    pairs: List[Tuple[str, str]] = [
        ("E1", "E2"),
        ("E2", "E3"),
        ("E5", "E8"),
        ("E6", "E4"),
        ("E7", "E5"),
        ("E7", "E9"),
    ]
    print(f"{'Event A':<10}{'Event B':<10}{'Vector A':<18}{'Vector B':<18}Relationship")
    for a_id, b_id in pairs:
        a, b = by_event[a_id], by_event[b_id]
        print(
            f"{a_id:<10}{b_id:<10}{fmt(a.timestamp):<18}"
            f"{fmt(b.timestamp):<18}{compare_vectors(a.timestamp, b.timestamp)}"
        )

    print("\nREQUIRED CASES")
    print("-" * 88)
    print("Case 1 — Same-process ordering: E1 -> E2")
    print(f"  {fmt(t_e1)} compared with {fmt(by_event['E2'].timestamp)}: "
          f"{compare_vectors(t_e1, by_event['E2'].timestamp)}")
    print("Case 2 — Message-based causality: SEND M1 (E2) -> RECEIVE M1 (E3)")
    print(f"  {fmt(by_event['E2'].timestamp)} compared with {fmt(t_e3)}: "
          f"{compare_vectors(by_event['E2'].timestamp, t_e3)}")
    print("Case 3 — Transitive causality: E2 -> E3 -> E5 -> E8 -> E9")
    print(f"  E2 {fmt(by_event['E2'].timestamp)} compared with E9 "
          f"{fmt(t_e9)}: {compare_vectors(by_event['E2'].timestamp, t_e9)}")

    print("\nCONCURRENT EVENTS DEMONSTRATION")
    print("-" * 88)
    # Independent local events in two fresh processes, with no messages between them.
    concurrent_log: List[Event] = []
    q1 = Process("Q1", 0, 2, concurrent_log)
    q2 = Process("Q2", 1, 2, concurrent_log)
    a = q1.local_event("A")
    b = q2.local_event("B")
    print(f"Event A at Q1: {fmt(a)}")
    print(f"Event B at Q2: {fmt(b)}")
    print(f"Comparison: {compare_vectors(a, b)}")
    print("Neither vector is component-wise <= the other, so the events are concurrent.")

    print("\nFINAL PROCESS VECTOR CLOCKS")
    for name, process in processes.items():
        print(f"{name}: {fmt(process.clock)}")


if __name__ == "__main__":
    main()
