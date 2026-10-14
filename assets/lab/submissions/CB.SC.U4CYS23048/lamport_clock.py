class Process:
    def __init__(self, name, all_events):
        self.name = name
        self.clock = 0
        self.all_events = all_events
        self.last_event = None
        self.messages = set()

    def add_event(self, event_type, message=None):
        parents = []

        if self.last_event is not None:
            parents.append(self.last_event)

        if event_type == "RECEIVE":
            parents.append(message["send_event"])

        event = {
            "event": "E" + str(len(self.all_events) + 1),
            "process": self.name,
            "type": event_type,
            "message": message["id"] if message else "-",
            "timestamp": self.clock,
            "parents": parents
        }

        self.all_events.append(event)
        self.last_event = event["event"]

        return event

    def local(self):
        self.clock += 1
        return self.add_event("LOCAL")

    def send(self, receiver, msg_id):
        if receiver == self.name:
            raise ValueError("Receiver must be different from sender")

        self.clock += 1

        message = {
            "id": msg_id,
            "sender": self.name,
            "receiver": receiver,
            "timestamp": self.clock
        }

        event = self.add_event("SEND", message)
        message["send_event"] = event["event"]

        return message

    def receive(self, message):
        if message["receiver"] != self.name:
            raise ValueError("Incorrect receiver")

        if message["id"] in self.messages:
            raise ValueError("Message already received")

        self.clock = max(self.clock, message["timestamp"]) + 1
        self.messages.add(message["id"])

        return self.add_event("RECEIVE", message)


def is_before(events, first_event, second_event):
    parents = {}

    for event in events:
        parents[event["event"]] = event["parents"]

    stack = list(parents[second_event])
    checked = set()

    while stack:
        current = stack.pop()

        if current == first_event:
            return True

        if current not in checked:
            checked.add(current)
            stack.extend(parents[current])

    return False


def create_events():
    events = []

    p1 = Process("P1", events)
    p2 = Process("P2", events)
    p3 = Process("P3", events)

    p1.local()

    message1 = p1.send("P2", "M1")
    p2.receive(message1)

    p2.local()

    message2 = p2.send("P3", "M2")

    p1.local()

    message3 = p1.send("P3", "M3")

    p3.receive(message2)
    p3.receive(message3)

    return events


def main():
    events = create_events()

    print("LAMPORT CLOCK\n")

    print(
        f"{'Event':<8} {'Process':<10} "
        f"{'Type':<10} {'Message':<10} {'Timestamp':>10}"
    )

    for event in events:
        print(
            f"{event['event']:<8} "
            f"{event['process']:<10} "
            f"{event['type']:<10} "
            f"{event['message']:<10} "
            f"{event['timestamp']:>10}"
        )

    print("\nCAUSAL RELATIONSHIPS")

    pairs = [
        ("E1", "E2"),
        ("E2", "E3"),
        ("E5", "E8"),
        ("E2", "E8"),
        ("E4", "E6")
    ]

    for first, second in pairs:

        if is_before(events, first, second):
            result = "happened before"

        elif is_before(events, second, first):
            result = "happened after"

        else:
            result = "is concurrent with"

        print(first, result, second)

    print(
        "\nConcurrency is determined from the event history, "
        "not from Lamport timestamps alone."
    )

    sorted_events = sorted(
        events,
        key=lambda x: (x["timestamp"], x["process"])
    )

    order = []

    for event in sorted_events:
        order.append(event["event"])

    print("Total order (timestamp, process): " + ", ".join(order))


if __name__ == "__main__":
    main()
