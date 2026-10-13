
class Process:
    def __init__(self, name):
        self.name = name
        self.clock = 0

    def localEvent(self, eventId):
        self.clock += 1
        return {
            "process": self.name,
            "event": eventId,
            "type": "Local",
            "timestamp": self.clock
        }

    def sendEvent(self, eventId, receiver):
        self.clock += 1

        message = {
            "messageId": f"msg_{eventId}",
            "sender": self.name,
            "receiver": receiver,
            "timestamp": self.clock
        }

        record = {
            "process": self.name,
            "event": eventId,
            "type": "Send",
            "timestamp": self.clock
        }

        return message, record

    def receiveEvent(self, eventId, message):
        self.clock = max(self.clock, message["timestamp"]) + 1

        return {
            "process": self.name,
            "event": eventId,
            "type": "Receive",
            "timestamp": self.clock
        }


def main():
    p1 = Process("P1")
    p2 = Process("P2")
    p3 = Process("P3")

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

    print("=" * 55)
    print("           LAMPORT LOGICAL CLOCK")
    print("=" * 55)

    print(f"{'Process':<10} {'Event':<10} {'Type':<12} {'Time':>8}")
    print("-" * 55)

    for item in eventList:
        print(
            f"{item['process']:<10} "
            f"{item['event']:<10} "
            f"{item['type']:<12} "
            f"{item['timestamp']:>8}"
        )

    print("-" * 55)


if __name__ == "__main__":
    main()
