p1, p2, p3 = 0, 0, 0

events = []
messages = {}


def local(clock):
    clock = clock + 1
    return clock


def send(clock):
    clock = clock + 1
    return clock


def receive(clock, t):
    clock = max(clock, t) + 1
    return clock


def record(process, event, event_type, timestamp):
    events.append({
        "process": process,
        "event": event,
        "type": event_type,
        "timestamp": timestamp
    })


def create_message(message_id, sender, receiver, timestamp):
    return {
        "id": message_id,
        "sender": sender,
        "receiver": receiver,
        "timestamp": timestamp
    }


print("=" * 65)
print("                 LAMPORT LOGICAL CLOCK")
print("=" * 65)

print(f"{'Process':<12}{'Event':<12}{'Type':<15}{'Timestamp'}")
print("-" * 65)


# E1: P1 performs a local event
p1 = local(p1)
e1 = p1
record("P1", "E1", "LOCAL", e1)
print(f"{'P1':<12}{'E1':<12}{'LOCAL':<15}{e1}")


p1 = send(p1)
e2 = p1

messages["M1"] = create_message("M1", "P1", "P2", p1)
m1 = messages["M1"]

record("P1", "E2", "SEND M1", e2)
print(f"{'P1':<12}{'E2':<12}{'SEND M1':<15}{e2}")


p2 = receive(p2, m1["timestamp"])
e3 = p2

record("P2", "E3", "RECEIVE M1", e3)
print(f"{'P2':<12}{'E3':<12}{'RECEIVE M1':<15}{e3}")


p2 = local(p2)
e4 = p2

record("P2", "E4", "LOCAL", e4)
print(f"{'P2':<12}{'E4':<12}{'LOCAL':<15}{e4}")


p2 = send(p2)
e5 = p2

messages["M2"] = create_message("M2", "P2", "P3", p2)
m2 = messages["M2"]

record("P2", "E5", "SEND M2", e5)
print(f"{'P2':<12}{'E5':<12}{'SEND M2':<15}{e5}")


p1 = local(p1)
e6 = p1

record("P1", "E6", "LOCAL", e6)
print(f"{'P1':<12}{'E6':<12}{'LOCAL':<15}{e6}")


p1 = send(p1)
e7 = p1

messages["M3"] = create_message("M3", "P1", "P3", p1)
m3 = messages["M3"]

record("P1", "E7", "SEND M3", e7)
print(f"{'P1':<12}{'E7':<12}{'SEND M3':<15}{e7}")


p3 = receive(p3, m2["timestamp"])
e8 = p3

record("P3", "E8", "RECEIVE M2", e8)
print(f"{'P3':<12}{'E8':<12}{'RECEIVE M2':<15}{e8}")


p3 = receive(p3, m3["timestamp"])
e9 = p3

record("P3", "E9", "RECEIVE M3", e9)
print(f"{'P3':<12}{'E9':<12}{'RECEIVE M3':<15}{e9}")


print("-" * 65)


print("\nMESSAGE DETAILS")
print("-" * 65)

for message in messages.values():
    print(
        f"Message ID: {message['id']} | "
        f"Sender: {message['sender']} | "
        f"Receiver: {message['receiver']} | "
        f"Timestamp: {message['timestamp']}"
    )


print("\nFINAL LOGICAL CLOCKS")
print("-" * 65)

print(f"P1 Clock = {p1}")
print(f"P2 Clock = {p2}")
print(f"P3 Clock = {p3}")


print("\nCAUSAL ORDERING")
print("-" * 75)

print(
    f"{'Event A':<20}{'Event B':<20}"
    f"{'Timestamp A':<15}{'Timestamp B':<15}{'Verified'}"
)
print("-" * 75)

causal_pairs = [
    ("P1 SEND M1", e2, "P2 RECEIVE M1", e3),
    ("P2 SEND M2", e5, "P3 RECEIVE M2", e8)
]

for event_a, time_a, event_b, time_b in causal_pairs:
    print(
        f"{event_a:<20}{event_b:<20}"
        f"{time_a:<15}{time_b:<15}{time_a < time_b}"
    )
print("\nCONCURRENT EVENTS")
print("-" * 65)

print(f"P2 E4 Timestamp = {e4}")
print(f"P1 E6 Timestamp = {e6}")


print("E4 and E6 are concurrent.")
print("Neither event causally precedes the other.")

print(
    "Lamport timestamps alone cannot determine "
    "whether two events are concurrent."
)

print("-" * 65)