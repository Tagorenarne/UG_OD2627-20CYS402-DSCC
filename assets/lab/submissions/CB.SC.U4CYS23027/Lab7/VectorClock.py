class Process:
    def __init__(self, name, index):
        self.name = name
        self.index = index          # position of this process in the vector
        self.clock = [0, 0, 0]
        self.events = []

    # Local event, increment own component
    def local_event(self, event_id):
        self.clock[self.index] += 1
        self.events.append((event_id, "LOCAL", "-", self.clock.copy()))

    # Send, increment own component, attach the vector to the message
    def send_message(self, receiver, message_id, event_id):
        self.clock[self.index] += 1

        message = {
            "id": message_id,
            "sender": self.name,
            "receiver": receiver.name,
            "timestamp": self.clock.copy()
        }

        self.events.append((event_id, "SEND", self.name + "->" + receiver.name, self.clock.copy()))
        return message

    # Receive, max with the message vector, then increment own component
    def receive_message(self, message, event_id):
        for j in range(3):
            self.clock[j] = max(self.clock[j], message["timestamp"][j])
        self.clock[self.index] += 1

        self.events.append((event_id, "RECEIVE", message["sender"] + "->" + self.name, self.clock.copy()))


# returns "->", "<-", "||" or "=="
def compare(v1, v2):
    v1_le_v2 = all(a <= b for a, b in zip(v1, v2))
    v2_le_v1 = all(b <= a for a, b in zip(v1, v2))

    if v1_le_v2 and v2_le_v1:
        return "=="
    if v1_le_v2:
        return "->"
    if v2_le_v1:
        return "<-"
    return "||"


# ==================================================
# creating p1,p2 and p3
# ==================================================

P1 = Process("P1", 0)
P2 = Process("P2", 1)
P3 = Process("P3", 2)

print("=" * 60)
print("                    VECTOR CLOCK")
print("=" * 60)

print("\nInitial Vector Clocks:")
print("P1 =", P1.clock)
print("P2 =", P2.clock)
print("P3 =", P3.clock)


# ==================================================
# executing the required events
# ==================================================

P1.local_event("E1")                    # E1
M1 = P1.send_message(P2, "M1", "E2")    # E2
P2.receive_message(M1, "E3")            # E3
P2.local_event("E4")                    # E4
M2 = P2.send_message(P3, "M2", "E5")    # E5
P1.local_event("E6")                    # E6
M3 = P1.send_message(P3, "M3", "E7")    # E7
P3.receive_message(M2, "E8")            # E8
P3.receive_message(M3, "E9")            # E9


# ==================================================
# event log 
# ==================================================

all_events = []
for p in [P1, P2, P3]:
    for event_id, event_type, msg, vector in p.events:
        all_events.append((event_id, p.name, event_type, msg, vector))
all_events.sort()

vec = {}    # event id -> vector, used for the comparisons below
for event_id, name, event_type, msg, vector in all_events:
    vec[event_id] = vector

print("\nEvent Log:")
print("-" * 60)
print(f"{'Process':<9}{'Event':<7}{'Type':<10}{'Message':<10}{'Vector'}")
print("-" * 60)
for event_id, name, event_type, msg, vector in all_events:
    print(f"{name:<9}{event_id:<7}{event_type:<10}{msg:<10}{vector}")
print("-" * 60)

print("\nFinal Vector Clocks:")
print("P1 =", P1.clock)
print("P2 =", P2.clock)
print("P3 =", P3.clock)


# ==================================================
# causal ordering / concurrency 
# ==================================================

def show(label, a, b):
    result = compare(vec[a], vec[b])
    if result == "->":
        text = a + " -> " + b
    elif result == "<-":
        text = b + " -> " + a
    elif result == "||":
        text = a + " || " + b + " (concurrent)"
    else:
        text = "same timestamp"
    print(f"{label:<14}{a} {vec[a]}  vs  {b} {vec[b]}   =>  {text}")


print("\nRequired Cases:")
print("-" * 60)
show("Same process", "E1", "E2")
show("Message", "E2", "E3")
show("Transitive", "E1", "E9")
show("Concurrent", "E6", "E4")

print("\nCausal Relationship Table:")
print("-" * 60)
for a, b in [("E1", "E2"), ("E2", "E3"), ("E5", "E8"), ("E6", "E4"), ("E7", "E5")]:
    show("", a, b)
