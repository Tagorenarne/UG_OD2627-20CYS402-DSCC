N = 3   # number of processes


class Process:
    def __init__(self, name, index):
        self.name = name
        self.index = index          # position of this process in the vector
        self.vector = [0] * N


events = {}        # event id -> (process, type, vector, message)
message_count = 0


def show(v):
    return "[" + ",".join(map(str, v)) + "]"


def record(process, event_type, message="-"):
    event_id = f"E{len(events) + 1}"
    events[event_id] = (process.name, event_type, process.vector.copy(), message)
    print(f"{process.name:<10} {event_id:<8} {event_type:<11} {show(process.vector):<12} {message}")


def local_event(process):
    process.vector[process.index] += 1                   # Rule 1
    record(process, "LOCAL")


def send_message(sender, receiver):
    global message_count
    message_count += 1
    sender.vector[sender.index] += 1                     # Rule 2
    message = {
        "id": f"M{message_count}",
        "sender": sender.name,
        "receiver": receiver.name,
        "vector": sender.vector.copy(),
    }
    record(sender, "SEND", f"{sender.name} -> {receiver.name} ({message['id']} carries {show(message['vector'])})")
    return message


def receive_message(receiver, message):
    for j in range(N):                                   # Rule 3
        receiver.vector[j] = max(receiver.vector[j], message["vector"][j])
    receiver.vector[receiver.index] += 1
    record(receiver, "RECEIVE", f"{message['sender']} -> {receiver.name} ({message['id']})")


def less_equal(v1, v2):
    return all(a <= b for a, b in zip(v1, v2))


def compare_vectors(v1, v2):
    if v1 == v2:
        return "V1 and V2 represent the same timestamp"
    if less_equal(v1, v2):
        return "V1 happened before V2"
    if less_equal(v2, v1):
        return "V2 happened before V1"
    return "V1 and V2 are concurrent"


P1, P2, P3 = Process("P1", 0), Process("P2", 1), Process("P3", 2)

print("=" * 75)
print("                           VECTOR CLOCK")
print("=" * 75)
print(f"\n{'Process':<10} {'Event':<8} {'Type':<11} {'Vector':<12} Message")
print("-" * 75)

local_event(P1)                  # 1. E1
m1 = send_message(P1, P2)        # 2. E2
receive_message(P2, m1)          # 3. E3
local_event(P2)                  # 4. E4
m2 = send_message(P2, P3)        # 5. E5
local_event(P1)                  # 6. E6
m3 = send_message(P1, P3)        # 7. E7
receive_message(P3, m2)          # 8. E8
receive_message(P3, m3)          # 9. E9

print("-" * 75)


def vc(event_id):
    return events[event_id][2]


# Required experiment: the four cases
print("\nCase 1 - Same Process Ordering (P1 E1 -> P1 E2)")
print(f"  VC(E1) = {show(vc('E1'))}, VC(E2) = {show(vc('E2'))}  =>  {compare_vectors(vc('E1'), vc('E2'))}")

print("\nCase 2 - Message-Based Causality (P1 SEND E2 -> P2 RECEIVE E3)")
print(f"  VC(E2) = {show(vc('E2'))}, VC(E3) = {show(vc('E3'))}  =>  {compare_vectors(vc('E2'), vc('E3'))}")

print("\nCase 3 - Transitive Causality (P1 E2 -> P2 E5 -> P3 E8)")
print(f"  VC(E2) = {show(vc('E2'))}, VC(E5) = {show(vc('E5'))}, VC(E8) = {show(vc('E8'))}")
print(f"  E2 vs E5 => {compare_vectors(vc('E2'), vc('E5'))}")
print(f"  E5 vs E8 => {compare_vectors(vc('E5'), vc('E8'))}")
print(f"  E2 vs E8 => {compare_vectors(vc('E2'), vc('E8'))}  (causality propagated through P2)")

print("\nCase 4 - Concurrent Events (A = E6 at P1, B = E4 at P2)")
a, b = vc("E6"), vc("E4")
print(f"  VC(A) = {show(a)}, VC(B) = {show(b)}")
print(f"  VC(A) <= VC(B) ? {less_equal(a, b)}")
print(f"  VC(B) <= VC(A) ? {less_equal(b, a)}")
print(f"  =>  {compare_vectors(a, b)}  (A || B)")

# Causal relationship table
symbols = {
    "V1 happened before V2": "A -> B",
    "V2 happened before V1": "B -> A",
    "V1 and V2 are concurrent": "A || B",
    "V1 and V2 represent the same timestamp": "A == B",
}
print("\nCausal Relationship Table\n")
print(f"{'Event A':<9} {'Event B':<9} {'Vector A':<10} {'Vector B':<10} Relationship")
print("-" * 55)
for ea, eb in [("E1", "E2"), ("E2", "E3"), ("E5", "E8"), ("E6", "E4"), ("E7", "E5")]:
    result = compare_vectors(vc(ea), vc(eb))
    print(f"{ea:<9} {eb:<9} {show(vc(ea)):<10} {show(vc(eb)):<10} {symbols[result]}")
