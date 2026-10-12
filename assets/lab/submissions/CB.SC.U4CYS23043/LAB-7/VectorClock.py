class Node:
    def __init__(self, node_name, position):
        self.node_name = node_name
        self.position = position          # position of the process in the vector
        self.vector_clock = [0, 0, 0]
        self.event_log = []

    # Local event, increment own component
    def create_local_event(self, event_name):
        self.vector_clock[self.position] += 1
        self.event_log.append((event_name, "LOCAL", "-", self.vector_clock.copy()))

    # Send, increment own component, attach the vector to the message
    def send_data(self, destination, msg_name, event_name):
        self.vector_clock[self.position] += 1

        packet = {
            "id": msg_name,
            "sender": self.node_name,
            "receiver": destination.node_name,
            "timestamp": self.vector_clock.copy()
        }

        self.event_log.append((event_name, "SEND", self.node_name + "->" + destination.node_name, self.vector_clock.copy()))
        return packet

    # Receive, max with the message vector, then increment own component
    def receive_data(self, packet, event_name):
        for k in range(3):
            self.vector_clock[k] = max(self.vector_clock[k], packet["timestamp"][k])
        self.vector_clock[self.position] += 1

        self.event_log.append((event_name, "RECEIVE", packet["sender"] + "->" + self.node_name, self.vector_clock.copy()))


# returns "->", "<-", "||" or "=="
def compare_vectors(clock_a, clock_b):
    a_before_b = all(x <= y for x, y in zip(clock_a, clock_b))
    b_before_a = all(y <= x for x, y in zip(clock_a, clock_b))

    if a_before_b and b_before_a:
        return "=="
    if a_before_b:
        return "->"
    if b_before_a:
        return "<-"
    return "||"


# ==================================================
# creating p1,p2 and p3
# ==================================================

NODE1 = Node("P1", 0)
NODE2 = Node("P2", 1)
NODE3 = Node("P3", 2)

print("=" * 60)
print("                    VECTOR CLOCK")
print("=" * 60)

print("\nInitial Vector Clocks:")
print("P1 =", NODE1.vector_clock)
print("P2 =", NODE2.vector_clock)
print("P3 =", NODE3.vector_clock)


# ==================================================
# executing the required events
# ==================================================

NODE1.create_local_event("E1")                    # E1
MSG1 = NODE1.send_data(NODE2, "M1", "E2")         # E2
NODE2.receive_data(MSG1, "E3")                    # E3
NODE2.create_local_event("E4")                    # E4
MSG2 = NODE2.send_data(NODE3, "M2", "E5")         # E5
NODE1.create_local_event("E6")                    # E6
MSG3 = NODE1.send_data(NODE3, "M3", "E7")         # E7
NODE3.receive_data(MSG2, "E8")                    # E8
NODE3.receive_data(MSG3, "E9")                    # E9


# ==================================================
# event log 
# ==================================================

combined_events = []
for node in [NODE1, NODE2, NODE3]:
    for event_name, event_type, message, timestamp in node.event_log:
        combined_events.append((event_name, node.node_name, event_type, message, timestamp))
combined_events.sort()

event_vectors = {}    # event id -> vector, used for the comparisons below
for event_name, node_name, event_type, message, timestamp in combined_events:
    event_vectors[event_name] = timestamp

print("\nEvent Log:")
print("-" * 60)
print(f"{'Process':<9}{'Event':<7}{'Type':<10}{'Message':<10}{'Vector'}")
print("-" * 60)
for event_name, node_name, event_type, message, timestamp in combined_events:
    print(f"{node_name:<9}{event_name:<7}{event_type:<10}{message:<10}{timestamp}")
print("-" * 60)

print("\nFinal Vector Clocks:")
print("P1 =", NODE1.vector_clock)
print("P2 =", NODE2.vector_clock)
print("P3 =", NODE3.vector_clock)


# ==================================================
# causal ordering / concurrency 
# ==================================================

def display_comparison(label, event_a, event_b):
    relation = compare_vectors(event_vectors[event_a], event_vectors[event_b])
    if relation == "->":
        description = event_a + " -> " + event_b
    elif relation == "<-":
        description = event_b + " -> " + event_a
    elif relation == "||":
        description = event_a + " || " + event_b + " (concurrent)"
    else:
        description = "same timestamp"
    print(f"{label:<14}{event_a} {event_vectors[event_a]}  vs  {event_b} {event_vectors[event_b]}   =>  {description}")


print("\nRequired Cases:")
print("-" * 60)
display_comparison("Same process", "E1", "E2")
display_comparison("Message", "E2", "E3")
display_comparison("Transitive", "E1", "E9")
display_comparison("Concurrent", "E6", "E4")

print("\nCausal Relationship Table:")
print("-" * 60)
for event_a, event_b in [("E1", "E2"), ("E2", "E3"), ("E5", "E8"), ("E6", "E4"), ("E7", "E5")]:
    display_comparison("", event_a, event_b)
