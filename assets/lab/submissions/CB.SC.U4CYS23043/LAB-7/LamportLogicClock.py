class Node:
    def __init__(self, process_name):
        self.process_name = process_name
        self.logical_clock = 0
        self.event_log = []

    # Local Event function
    # clock increments by one
    def create_local_event(self, event_name):
        self.logical_clock += 1
        self.event_log.append((event_name, "LOCAL", self.logical_clock))

    # Send Message function
    #sender increments its clock before sending
    def transmit_message(self, destination, msg_name):
        self.logical_clock += 1

        packet = {
            "id": msg_name,
            "sender": self.process_name,
            "receiver": destination.process_name,
            "timestamp": self.logical_clock
        }

        self.event_log.append((msg_name, "SEND", self.logical_clock))
        return packet

    # Receive Message function
    # so if p1 is sending msg to p2, we take the max of p2's time and p1's timestamp
    def accept_message(self, packet, event_name):
        incoming_timestamp = packet["timestamp"]

        self.logical_clock = max(self.logical_clock, incoming_timestamp) + 1

        self.event_log.append((event_name, "RECEIVE", self.logical_clock))


# ==================================================
# creating p1,p2 and p3 
# ==================================================

NODE1 = Node("P1")
NODE2 = Node("P2")
NODE3 = Node("P3")


print("=" * 60)
print("             LAMPORT LOGICAL CLOCK")
print("=" * 60)
# initially all 3 r 0
print("\nInitial Logical Clocks:")
print("P1 =", NODE1.logical_clock)
print("P2 =", NODE2.logical_clock)
print("P3 =", NODE3.logical_clock)

print("\nEvent Execution:")
print("-" * 60)


# ==================================================
# exxecuting the required events
# ==================================================

# 1. P1 performs local event E1
NODE1.create_local_event("E1") #p1 =1

# 2. P1 sends message M1 to P2
MSG1 = NODE1.transmit_message(NODE2, "M1") # p1 =2 and p2 = 0

# 3. P2 receives message M1
NODE2.accept_message(MSG1, "E3") # max(0,2)+1

# 4. P2 performs local event E4
NODE2.create_local_event("E4") # 3+1=4

# 5. P2 sends message M2 to P3
MSG2 = NODE2.transmit_message(NODE3, "M2")#p2 = 4+1=5

# 6. P1 performs local event E6
NODE1.create_local_event("E6") # p1 = 2+1 =3

# 7. P1 sends message M3 to P3
MSG3 = NODE1.transmit_message(NODE3, "M3") # 3+1=4

# 8. P3 receives message M2 from P2
NODE3.accept_message(MSG2, "E8") #5+1=6

# 9. P3 receives message M3 from P1
NODE3.accept_message(MSG3, "E9") # 6+1=7


# ==================================================
# DISPLAY EVENT LOG
# ==================================================

print("\nEvent Log:")
print("-" * 60)

print(f"{'Process':<10}{'Event':<10}{'Type':<12}{'Timestamp':<10}")
print("-" * 60)

for node in [NODE1, NODE2, NODE3]:
    for event in node.event_log:
        event_name, event_type, timestamp = event
        print(
            f"{node.process_name:<10}"
            f"{event_name:<10}"
            f"{event_type:<12}"
            f"{timestamp:<10}"
        )


# ==================================================
# finalll clockss
# ==================================================

print("-" * 60)

print("\nFinal Logical Clocks:")
print("P1 =", NODE1.logical_clock)
print("P2 =", NODE2.logical_clock)
print("P3 =", NODE3.logical_clock)


# ==================================================
# casual
# ==================================================

print("\nCausal Ordering:")
print("-" * 60)      

print("P1 SEND M1  ->  P2 RECEIVE M1")
print("Timestamp: 2 < 3")

print("P2 SEND M2  ->  P3 RECEIVE M2")
print("Timestamp: 5 < 6")


# ==================================================
# CONCURRENT EVENTS
# ==================================================

print("\nConcurrent Events:")
print("-" * 60)

print("P1 E6 Timestamp =", NODE1.event_log[1][2])
print("P2 E4 Timestamp =", NODE2.event_log[1][2])
