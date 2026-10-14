class Process:
    def __init__(self, name, position, events):
        self.name = name
        self.position = position
        self.clock = [0, 0, 0]
        self.events = events
        self.received = set()

    def save_event(self, event_type, message=None):
        event = {
            "event": "E" + str(len(self.events) + 1),
            "process": self.name,
            "type": event_type,
            "message": message["id"] if message else "-",
            "timestamp": self.clock.copy()
        }

        self.events.append(event)
        return event

    def local(self):
        self.clock[self.position] += 1
        return self.save_event("LOCAL")

    def send(self, receiver, message_id):
        if receiver == self.name:
            raise ValueError("Receiver must be different")

        self.clock[self.position] += 1

        message = {
            "id": message_id,
            "sender": self.name,
            "receiver": receiver,
            "timestamp": self.clock.copy()
        }

        self.save_event("SEND", message)

        return message

    def receive(self, message):
        if message["receiver"] != self.name:
            raise ValueError("Wrong receiver")

        if message["id"] in self.received:
            raise ValueError("Message already received")

        received_clock = message["timestamp"]

        if len(received_clock) != len(self.clock):
            raise ValueError("Invalid vector")

        for i in range(len(self.clock)):
            if received_clock[i] > self.clock[i]:
                self.clock[i] = received_clock[i]

        self.clock[self.position] += 1
        self.received.add(message["id"])

        return self.save_event("RECEIVE", message)


def compare_vectors(a, b):

    if len(a) != len(b):
        raise ValueError("Vector sizes are different")

    if a == b:
        return "same timestamp"

    a_less = True
    b_less = True

    for i in range(len(a)):
        if a[i] > b[i]:
            a_less = False

        if a[i] < b[i]:
            b_less = False

    if a_less:
        return "happened before"

    if b_less:
        return "happened after"

    return "is concurrent with"


def simulate():
    events = []

    p1 = Process("P1", 0, events)
    p2 = Process("P2", 1, events)
    p3 = Process("P3", 2, events)

    p1.local()

    m1 = p1.send("P2", "M1")
    p2.receive(m1)

    p2.local()

    m2 = p2.send("P3", "M2")

    p1.local()

    m3 = p1.send("P3", "M3")

    p3.receive(m2)
    p3.receive(m3)

    return events


def main():
    events = simulate()

    print("VECTOR CLOCK\n")

    print(
        f"{'Event':<8} {'Process':<10} "
        f"{'Type':<10} {'Message':<10} Vector"
    )

    for event in events:
        print(
            f"{event['event']:<8}"
            f"{event['process']:<10}"
            f"{event['type']:<10}"
            f"{event['message']:<10}"
            f"{event['timestamp']}"
        )

    print("\nCAUSAL RELATIONSHIPS")

    clocks = {}

    for event in events:
        clocks[event["event"]] = event["timestamp"]

    checks = [
        ("E1", "E2"),
        ("E2", "E3"),
        ("E5", "E8"),
        ("E2", "E8"),
        ("E6", "E4"),
        ("E7", "E5")
    ]

    for first, second in checks:
        relation = compare_vectors(
            clocks[first],
            clocks[second]
        )

        print(
            first,
            clocks[first],
            relation,
            second,
            clocks[second]
        )


if __name__ == "__main__":
    main()
