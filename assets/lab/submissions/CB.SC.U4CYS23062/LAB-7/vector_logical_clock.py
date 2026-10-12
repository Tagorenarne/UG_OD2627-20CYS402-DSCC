p1, p2, p3 = [0, 0, 0], [0, 0, 0], [0, 0, 0]

events = []
messages = {}


def local(clock, index):
    clock[index] += 1
    return clock


def send(clock, index):
    clock[index] += 1
    return clock


def receive(clock, timestamp, index):
    for i in range(len(clock)):
        clock[i] = max(clock[i], timestamp[i])

    clock[index] += 1
    return clock


def record(process, event, event_type, timestamp):
    events.append({
        "process": process,
        "event": event,
        "type": event_type,
        "timestamp": timestamp.copy()
    })


def create_message(message_id, sender, receiver, timestamp):
    return {
        "id": message_id,
        "sender": sender,
        "receiver": receiver,
        "timestamp": timestamp.copy()
    }


def compare_vectors(a, b):
    a_before_b = (
        all(x <= y for x, y in zip(a, b))
        and any(x < y for x, y in zip(a, b))
    )

    b_before_a = (
        all(x <= y for x, y in zip(b, a))
        and any(x < y for x, y in zip(b, a))
    )

    if a_before_b:
        return "A -> B"
    elif b_before_a:
        return "B -> A"
    elif a == b:
        return "EQUAL"
    else:
        return "CONCURRENT"


print("=" * 75)
print("                     VECTOR CLOCK")
print("=" * 75)

print(f"{'Process':<12}{'Event':<12}{'Type':<15}{'Vector Timestamp'}")
print("-" * 75)


p1 = local(p1, 0)
e1 = p1.copy()

record("P1", "E1", "LOCAL", e1)
print(f"{'P1':<12}{'E1':<12}{'LOCAL':<15}{e1}")


p1 = send(p1, 0)
e2 = p1.copy()

messages["M1"] = create_message("M1", "P1", "P2", p1)
m1 = messages["M1"]

record("P1", "E2", "SEND M1", e2)
print(f"{'P1':<12}{'E2':<12}{'SEND M1':<15}{e2}")


p2 = receive(p2, m1["timestamp"], 1)
e3 = p2.copy()

record("P2", "E3", "RECEIVE M1", e3)
print(f"{'P2':<12}{'E3':<12}{'RECEIVE M1':<15}{e3}")


p2 = local(p2, 1)
e4 = p2.copy()

record("P2", "E4", "LOCAL", e4)
print(f"{'P2':<12}{'E4':<12}{'LOCAL':<15}{e4}")


p2 = send(p2, 1)
e5 = p2.copy()

messages["M2"] = create_message("M2", "P2", "P3", p2)
m2 = messages["M2"]

record("P2", "E5", "SEND M2", e5)
print(f"{'P2':<12}{'E5':<12}{'SEND M2':<15}{e5}")


p1 = local(p1, 0)
e6 = p1.copy()

record("P1", "E6", "LOCAL", e6)
print(f"{'P1':<12}{'E6':<12}{'LOCAL':<15}{e6}")


p1 = send(p1, 0)
e7 = p1.copy()

messages["M3"] = create_message("M3", "P1", "P3", p1)
m3 = messages["M3"]

record("P1", "E7", "SEND M3", e7)
print(f"{'P1':<12}{'E7':<12}{'SEND M3':<15}{e7}")


p3 = receive(p3, m2["timestamp"], 2)
e8 = p3.copy()

record("P3", "E8", "RECEIVE M2", e8)
print(f"{'P3':<12}{'E8':<12}{'RECEIVE M2':<15}{e8}")


p3 = receive(p3, m3["timestamp"], 2)
e9 = p3.copy()

record("P3", "E9", "RECEIVE M3", e9)
print(f"{'P3':<12}{'E9':<12}{'RECEIVE M3':<15}{e9}")


print("-" * 75)


print("\nMESSAGE DETAILS")
print("-" * 75)

for message in messages.values():
    print(
        f"Message ID: {message['id']} | "
        f"Sender: {message['sender']} | "
        f"Receiver: {message['receiver']} | "
        f"Timestamp: {message['timestamp']}"
    )


print("\nFINAL VECTOR CLOCKS")
print("-" * 75)

print(f"P1 Clock = {p1}")
print(f"P2 Clock = {p2}")
print(f"P3 Clock = {p3}")


print("\nCAUSAL ORDERING")
print("-" * 75)

causal_pairs = [
    ("E1", e1, "E2", e2),
    ("E2", e2, "E3", e3),
    ("E5", e5, "E8", e8),
    ("E2", e2, "E8", e8)
]

print(f"{'Event A':<12}{'Timestamp A':<20}"
      f"{'Event B':<12}{'Timestamp B':<20}{'Relationship'}")

print("-" * 75)

for name_a, time_a, name_b, time_b in causal_pairs:
    relationship = compare_vectors(time_a, time_b)

    print(
        f"{name_a:<12}{str(time_a):<20}"
        f"{name_b:<12}{str(time_b):<20}{relationship}"
    )


# Display concurrent events
print("\nCONCURRENT EVENTS")
print("-" * 75)

print(f"E4 Timestamp = {e4}")
print(f"E6 Timestamp = {e6}")
print("Relationship:", compare_vectors(e4, e6))

print()

print(f"E7 Timestamp = {e7}")
print(f"E5 Timestamp = {e5}")
print("Relationship:", compare_vectors(e7, e5))


print("\nVECTOR CLOCK COMPARISON")
print("-" * 75)

a = [3, 0, 0]
b = [2, 2, 0]

print("Vector A =", a)
print("Vector B =", b)
print("Relationship:", compare_vectors(a, b))

print("-" * 75)