
from dataclasses import dataclass


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


class Process:
    def __init__(self, name):
        self.name = name
        self.clock = 0
        self.events = []

    def record_event(self, event_id, event_type):
        event = Event(
            self.name,
            event_id,
            event_type,
            self.clock
        )
        self.events.append(event)

        print(
            f"{self.name:<10} "
            f"{event_id:<10} "
            f"{event_type:<10} "
            f"{self.clock}"
        )

        return event

    def local_event(self, event_id):
        self.clock += 1
        return self.record_event(event_id, "LOCAL")

    def send_message(self, receiver, message_id):
        self.clock += 1

        event = self.record_event(message_id, "SEND")

        message = Message(
            message_id,
            self.name,
            receiver.name,
            self.clock
        )

        print(
            f"   Message {message_id}: "
            f"{self.name} -> {receiver.name}, "
            f"Timestamp = {message.timestamp}"
        )

        return message, event

    def receive_message(self, message, event_id):
        if message.receiver != self.name:
            raise ValueError("Incorrect message receiver")

        self.clock = max(
            self.clock,
            message.timestamp
        ) + 1

        event = self.record_event(event_id, "RECEIVE")

        print(
            f"   Received {message.message_id} "
            f"from {message.sender}, "
            f"Message Timestamp = {message.timestamp}"
        )

        return event


def main():
    p1 = Process("P1")
    p2 = Process("P2")
    p3 = Process("P3")

    print("=" * 55)
    print("          LAMPORT LOGICAL CLOCK")
    print("=" * 55)
    print(f"{'Process':<10}{'Event':<10}{'Type':<10}Timestamp")
    print("-" * 55)

    # 1. P1 performs local event E1
    p1.local_event("E1")

    # 2. P1 sends M1 to P2
    m1, send_m1 = p1.send_message(p2, "M1")

    # 3. P2 receives M1
    recv_m1 = p2.receive_message(m1, "E3")

    # 4. P2 performs local event E4
    p2.local_event("E4")

    # 5. P2 sends M2 to P3
    m2, send_m2 = p2.send_message(p3, "M2")

    # 6. P1 performs local event E6
    p1.local_event("E6")

    # 7. P1 sends M3 to P3
    m3, send_m3 = p1.send_message(p3, "M3")

    # 8. P3 receives M2 from P2
    recv_m2 = p3.receive_message(m2, "E8")

    # 9. P3 receives M3 from P1
    recv_m3 = p3.receive_message(m3, "E9")

    print("\n" + "=" * 55)
    print("          CAUSAL ORDERING CHECKS")
    print("=" * 55)

    relationships = [
        ("P1 SEND M1", send_m1, "P2 RECEIVE M1", recv_m1),
        ("P2 SEND M2", send_m2, "P3 RECEIVE M2", recv_m2),
        ("P1 SEND M3", send_m3, "P3 RECEIVE M3", recv_m3),
    ]

    for name_a, event_a, name_b, event_b in relationships:
        valid = event_a.timestamp < event_b.timestamp

        print(f"{name_a} ({event_a.timestamp})")
        print(f"    -> {name_b} ({event_b.timestamp})")
        print(f"    Causal ordering valid: {valid}\n")

    print("=" * 55)
    print("       CONCURRENT EVENTS DEMONSTRATION")
    print("=" * 55)

    # Independent events on two processes, with no messages
    independent_p1 = Process("P1")
    independent_p2 = Process("P2")

    event_a = independent_p1.local_event("C1")
    event_b = independent_p2.local_event("C2")

    print(
        f"\nC1 timestamp = {event_a.timestamp}, "
        f"C2 timestamp = {event_b.timestamp}"
    )
    print("No message or causal dependency exists between C1 and C2.")
    print("Therefore, these events are concurrent.")

    print("\n" + "=" * 55)
    print("              FINAL CLOCKS")
    print("=" * 55)
    print(f"P1 Clock = {p1.clock}")
    print(f"P2 Clock = {p2.clock}")
    print(f"P3 Clock = {p3.clock}")
    print("\nLamport clock simulation completed successfully.")


if __name__ == "__main__":
    main()
