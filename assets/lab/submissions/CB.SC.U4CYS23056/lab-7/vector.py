
class Process:
    def __init__(self, name, index, n):
        self.name = name
        self.index = index
        self.clock = [0] * n

    def localEvent(self, eventId):
        self.clock[self.index] += 1
        return {
            "process": self.name,
            "event": eventId,
            "type": "LOCAL",
            "message": "-",
            "timestamp": self.clock.copy()
        }

    def sendEvent(self, eventId, receiver):
        self.clock[self.index] += 1

        message = {
            "messageId": f"msg_{eventId}",
            "sender": self.name,
            "receiver": receiver,
            "timestamp": self.clock.copy()
        }

        record = {
            "process": self.name,
            "event": eventId,
            "type": "SEND",
            "message": f"{self.name}->{receiver}",
            "timestamp": self.clock.copy()
        }

        return message, record

    def receiveEvent(self, eventId, message):
        self.clock = [
            max(a, b)
            for a, b in zip(self.clock, message["timestamp"])
        ]
        self.clock[self.index] += 1

        return {
            "process": self.name,
            "event": eventId,
            "type": "RECEIVE",
            "message": f"{message['sender']}->{self.name}",
            "timestamp": self.clock.copy()
        }


def compareVectors(v1, v2):
    lessEqual = all(a <= b for a, b in zip(v1, v2))
    greaterEqual = all(a >= b for a, b in zip(v1, v2))

    if lessEqual and greaterEqual:
        return "SAME"
    if lessEqual:
        return "V1 -> V2"
    if greaterEqual:
        return "V2 -> V1"
    return "V1 || V2"


def formatVector(vector):
    return "[" + ",".join(map(str, vector)) + "]"


def main():
    n = 3

    p1 = Process("P1", 0, n)
    p2 = Process("P2", 1, n)
    p3 = Process("P3", 2, n)

    eventList = []

    eventList.append(p1.localEvent("E1"))

    msg1, e2 = p1.sendEvent("E2", p2.name)
    eventList.append(e2)

    eventList.append(p2.receiveEvent("E3", msg1))

    eventList.append(p2.localEvent("E4"))

    msg2, e5 = p2.sendEvent("E5", p3.name)
    eventList.append(e5)

    eventList.append(p1.localEvent("E6"))

    msg3, e7 = p1.sendEvent("E7", p3.name)
    eventList.append(e7)

    eventList.append(p3.receiveEvent("E8", msg2))
    eventList.append(p3.receiveEvent("E9", msg3))

    print("=" * 60)
    print("              VECTOR LOGICAL CLOCK")
    print("=" * 60)

    print(
        f"{'Process':<10} {'Event':<8} {'Type':<12} "
        f"{'Message':<10} {'Timestamp':>12}"
    )
    print("-" * 60)

    for item in eventList:
        print(
            f"{item['process']:<10} "
            f"{item['event']:<8} "
            f"{item['type']:<12} "
            f"{item['message']:<10} "
            f"{formatVector(item['timestamp']):>12}"
        )

    print("-" * 60)

    timestamps = {
        item["event"]: item["timestamp"]
        for item in eventList
    }

    print("\n" + "=" * 60)
    print("              CAUSAL RELATIONSHIPS")
    print("=" * 60)

    print(
        f"{'Event A':<9} {'Event B':<9} "
        f"{'Vector A':>10} {'Vector B':>10}   Relationship"
    )
    print("-" * 70)

    pairs = [
        ("E1", "E2", "Same process ordering"),
        ("E2", "E3", "Message based causality"),
        ("E1", "E9", "Transitive causality"),
        ("E5", "E8", "Message based causality"),
        ("E6", "E4", "Concurrent events"),
        ("E7", "E5", "Concurrent events"),
        ("E8", "E9", "Same process ordering")
    ]

    for a, b, note in pairs:
        result = compareVectors(timestamps[a], timestamps[b])
        result = result.replace("V1", a).replace("V2", b)

        print(
            f"{a:<9} {b:<9} "
            f"{formatVector(timestamps[a]):>10} "
            f"{formatVector(timestamps[b]):>10}   "
            f"{result:<12} ({note})"
        )

    print("-" * 70)


if __name__ == "__main__":
    main()
