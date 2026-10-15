"""
20CYS402 - Distributed Systems and Cloud Computing
Lab #7A - Lamport Logical Clock

Simulates three distributed processes (P1, P2, P3) and demonstrates:
- Local, send, and receive events
- Lamport timestamp updates
- Message passing with timestamps
- Causal ordering
- Concurrent events and the limitation of scalar Lamport clocks
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Message:
    message_id: str
    sender: str
    receiver: str
    timestamp: int


@dataclass
class Event:
    process: str
    event_id: str
    event_type: str
    timestamp: int
    details: str = ""


class Process:
    def __init__(self, name: str, event_log: List[Event]):
        self.name = name
        self.clock = 0
        self.event_log = event_log

    def local_event(self, event_id: str) -> int:
        self.clock += 1
        self.event_log.append(Event(self.name, event_id, "LOCAL", self.clock))
        return self.clock

    def send_message(self, receiver: "Process", message_id: str) -> Message:
        self.clock += 1
        message = Message(message_id, self.name, receiver.name, self.clock)
        self.event_log.append(
            Event(self.name, message_id, "SEND", self.clock,
                  f"to {receiver.name}; message timestamp={message.timestamp}")
        )
        return message

    def receive_message(self, message: Message, event_id: str) -> int:
        if message.receiver != self.name:
            raise ValueError(
                f"Message {message.message_id} is addressed to {message.receiver}, "
                f"not {self.name}"
            )
        self.clock = max(self.clock, message.timestamp) + 1
        self.event_log.append(
            Event(self.name, event_id, "RECEIVE", self.clock,
                  f"from {message.sender}; received timestamp={message.timestamp}")
        )
        return self.clock


def print_event_log(events: List[Event]) -> None:
    print("=" * 72)
    print("                       LAMPORT LOGICAL CLOCK")
    print("=" * 72)
    print(f"{'Process':<10}{'Event':<10}{'Type':<12}{'Timestamp':<12}Details")
    print("-" * 72)
    for event in events:
        print(
            f"{event.process:<10}{event.event_id:<10}{event.event_type:<12}"
            f"{event.timestamp:<12}{event.details}"
        )
    print("-" * 72)


def main() -> None:
    events: List[Event] = []
    processes: Dict[str, Process] = {
        name: Process(name, events) for name in ("P1", "P2", "P3")
    }

    p1, p2, p3 = processes["P1"], processes["P2"], processes["P3"]

    # Required exercise sequence. Timestamps are calculated by the algorithm.
    p1.local_event("E1")
    m1 = p1.send_message(p2, "M1")
    p2.receive_message(m1, "E3")
    p2.local_event("E4")
    m2 = p2.send_message(p3, "M2")
    p1.local_event("E6")
    m3 = p1.send_message(p3, "M3")
    p3.receive_message(m2, "E8")
    p3.receive_message(m3, "E9")

    print_event_log(events)

    print("\nCAUSAL ORDERING CHECKS")
    print("-" * 72)
    by_id = {(e.process, e.event_id): e for e in events}
    causal_pairs = [
        ("P1 SEND M1", by_id[("P1", "M1")], "P2 RECEIVE E3", by_id[("P2", "E3")]),
        ("P2 SEND M2", by_id[("P2", "M2")], "P3 RECEIVE E8", by_id[("P3", "E8")]),
        ("P1 SEND M3", by_id[("P1", "M3")], "P3 RECEIVE E9", by_id[("P3", "E9")]),
    ]
    print(f"{'Event A':<18}{'Event B':<20}{'Timestamp A':<14}{'Timestamp B':<14}A < B?")
    for label_a, event_a, label_b, event_b in causal_pairs:
        print(
            f"{label_a:<18}{label_b:<20}{event_a.timestamp:<14}"
            f"{event_b.timestamp:<14}{event_a.timestamp < event_b.timestamp}"
        )

    print("\nCONCURRENT EVENTS DEMONSTRATION")
    print("-" * 72)
    # These two events occur on separate processes without any message path
    # between them. They are concurrent in the happened-before relation.
    concurrent_events: List[Event] = []
    q1 = Process("Q1", concurrent_events)
    q2 = Process("Q2", concurrent_events)
    q1.local_event("C1")
    q2.local_event("C2")
    print(f"Q1 event C1 timestamp = {concurrent_events[0].timestamp}")
    print(f"Q2 event C2 timestamp = {concurrent_events[1].timestamp}")
    print("There is no message or causal path between C1 and C2, so they are concurrent.")
    print("Lamport timestamps alone cannot prove concurrency: L(a) < L(b)")
    print("does not necessarily mean a happened before b.")

    print("\nFINAL PROCESS CLOCKS")
    for name, process in processes.items():
        print(f"{name}: {process.clock}")


if __name__ == "__main__":
    main()
