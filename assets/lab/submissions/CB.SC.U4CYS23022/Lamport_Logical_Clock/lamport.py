class Process:
    def __init__(self, name):
        self.name = name
        self.clock = 0


events = {}        # event id -> (process, type, timestamp)
message_count = 0


def record(process, event_type, details=""):
    event_id = f"E{len(events) + 1}"
    events[event_id] = (process.name, event_type, process.clock)
    print(f"{process.name:<10} {event_id:<8} {event_type:<10} {process.clock:>5}     {details}")


def local_event(process):
    process.clock += 1                                   # Rule 1
    record(process, "LOCAL")


def send_message(sender, receiver):
    global message_count
    message_count += 1
    sender.clock += 1                                    # Rule 2
    message = {
        "id": f"M{message_count}",
        "sender": sender.name,
        "receiver": receiver.name,
        "timestamp": sender.clock,
    }
    record(sender, "SEND", f"{message['id']} to {receiver.name}, timestamp = {message['timestamp']}")
    return message


def receive_message(receiver, message):
    T = message["timestamp"]
    receiver.clock = max(receiver.clock, T) + 1          # Rule 3
    record(receiver, "RECEIVE", f"{message['id']} from {message['sender']}, max(C, {T}) + 1")


P1, P2, P3 = Process("P1"), Process("P2"), Process("P3")

print("=" * 70)
print("                     LAMPORT LOGICAL CLOCK")
print("=" * 70)
print(f"\n{'Process':<10} {'Event':<8} {'Type':<10} {'Timestamp':<9} Details")
print("-" * 70)

local_event(P1)                  # 1. E1
m1 = send_message(P1, P2)        # 2. E2
receive_message(P2, m1)          # 3. E3
local_event(P2)                  # 4. E4
m2 = send_message(P2, P3)        # 5. E5
local_event(P1)                  # 6. E6
m3 = send_message(P1, P3)        # 7. E7
receive_message(P3, m2)          # 8. E8
receive_message(P3, m3)          # 9. E9

print("-" * 70)

# Causal ordering: a -> b  implies  L(a) < L(b)
print("\nCausal Ordering\n")
print(f"{'Event A':<16} {'Event B':<18} {'TS A':>5} {'TS B':>5}   L(A) < L(B)")
print("-" * 60)
for a, b, label_a, label_b in [("E2", "E3", "P1 SEND M1", "P2 RECEIVE M1"),
                               ("E5", "E8", "P2 SEND M2", "P3 RECEIVE M2"),
                               ("E7", "E9", "P1 SEND M3", "P3 RECEIVE M3")]:
    ta, tb = events[a][2], events[b][2]
    print(f"{label_a:<16} {label_b:<18} {ta:>5} {tb:>5}   {ta < tb}")

# Concurrent events: E4 (P2) and E6 (P1) have no causal path between them
print("\nConcurrent Events\n")
print(f"E4 (P2 LOCAL) timestamp = {events['E4'][2]}")
print(f"E6 (P1 LOCAL) timestamp = {events['E6'][2]}")
print("No message connects E4 and E6, so they are concurrent (E4 || E6).")
print("But their timestamps are different, so they look ordered.")
print("So Lamport timestamps alone CANNOT tell whether two events are concurrent.")
