from dataclasses import dataclass
from typing import List


@dataclass
class Message:
    message_id: str
    sender: str
    receiver: str
    vector_timestamp: List[int]


@dataclass
class Event:
    event_id: str
    process: str
    event_type: str
    vector_timestamp: List[int]
    message: str = "-"


class Process:
    def __init__(self, name: str, index: int, process_count: int = 3):
        self.name = name
        self.index = index
        self.vector = [0] * process_count
        self.events: List[Event] = []

    def _record(self, event_id: str, event_type: str, message: str = "-") -> Event:
        event = Event(
            event_id=event_id,
            process=self.name,
            event_type=event_type,
            vector_timestamp=self.vector.copy(),
            message=message,
        )
        self.events.append(event)
        print(
            f"{event.event_id:<7} {event.process:<8} {event.event_type:<9} "
            f"{event.message:<12} {event.vector_timestamp}"
        )
        return event

    def local_event(self, event_id: str) -> Event:
        self.vector[self.index] += 1
        return self._record(event_id, "LOCAL")

    def send_message(self, receiver: "Process", message_id: str):
        self.vector[self.index] += 1
        event = self._record(
            event_id=message_id,
            event_type="SEND",
            message=f"{self.name} -> {receiver.name}",
        )
        message = Message(
            message_id=message_id,
            sender=self.name,
            receiver=receiver.name,
            vector_timestamp=self.vector.copy(),
        )
        print(
            f"        Message {message.message_id}: {message.sender} -> "
            f"{message.receiver}, vector={message.vector_timestamp}"
        )
        return message, event

    def receive_message(self, message: Message, event_id: str) -> Event:
        if message.receiver != self.name:
            raise ValueError(
                f"{message.message_id} is addressed to {message.receiver}, not {self.name}"
            )

        self.vector = [
            max(local_value, received_value)
            for local_value, received_value in zip(
                self.vector, message.vector_timestamp
            )
        ]
        self.vector[self.index] += 1

        return self._record(
            event_id=event_id,
            event_type="RECEIVE",
            message=f"{message.sender} -> {self.name}",
        )


def compare_vectors(a: List[int], b: List[int]) -> str:
    """Return causal order, concurrency, or equality for two vector timestamps."""
    if len(a) != len(b):
        raise ValueError("Vector clocks must have the same length")

    a_le_b = all(x <= y for x, y in zip(a, b))
    b_le_a = all(y <= x for x, y in zip(a, b))

    if a_le_b and b_le_a:
        return "SAME VECTOR TIMESTAMP"
    if a_le_b:
        return "A happened before B (A -> B)"
    if b_le_a:
        return "B happened before A (B -> A)"
    return "CONCURRENT (A || B)"


def print_comparison(label: str, a: Event, b: Event) -> None:
    relation = compare_vectors(a.vector_timestamp, b.vector_timestamp)
    print(f"{label}")
    print(f"  A: {a.event_id} {a.vector_timestamp}")
    print(f"  B: {b.event_id} {b.vector_timestamp}")
    print(f"  Result: {relation}\n")


def main():
    p1 = Process("P1", 0)
    p2 = Process("P2", 1)
    p3 = Process("P3", 2)

    print("=" * 76)
    print("                         VECTOR CLOCK - LAB 8B")
    print("=" * 76)
    print("Event   Process  Type      Message      Vector Timestamp")
    print("-" * 76)

    e1 = p1.local_event("E1")
    m1, e2 = p1.send_message(p2, "E2")
    e3 = p2.receive_message(m1, "E3")
    e4 = p2.local_event("E4")
    m2, e5 = p2.send_message(p3, "E5")
    e6 = p1.local_event("E6")
    m3, e7 = p1.send_message(p3, "E7")
    e8 = p3.receive_message(m2, "E8")
    e9 = p3.receive_message(m3, "E9")

    print("-" * 76)
    print("FINAL VECTOR CLOCKS")
    print(f"P1: {p1.vector}")
    print(f"P2: {p2.vector}")
    print(f"P3: {p3.vector}")

    print("\n" + "=" * 76)
    print("VECTOR COMPARISON AND CAUSAL ORDERING")
    print("=" * 76)

    print_comparison("Case 1: Same-process ordering (E1 vs E2)", e1, e2)
    print_comparison("Case 2: Message causality (E2 vs E3)", e2, e3)
    print_comparison("Case 3: Transitive causality (E2 vs E8)", e2, e8)
    print_comparison("Case 4: E6 vs E4", e6, e4)
    print_comparison("Case 5: E7 vs E5", e7, e5)

    print("=" * 76)
    print("CONCURRENT EVENTS DEMONSTRATION")
    print("=" * 76)

    independent_p1 = Process("P1", 0)
    independent_p2 = Process("P2", 1)
    a = independent_p1.local_event("A")
    b = independent_p2.local_event("B")
    print_comparison("Independent local events A and B", a, b)

    print("Vector clock simulation completed.")


if __name__ == "__main__":
    main()
