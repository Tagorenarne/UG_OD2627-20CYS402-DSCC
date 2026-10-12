from lamport_clock import Process

#3 distributed processes
p1 = Process("P1")
p2 = Process("P2")
p3 = Process("P3")

print("==================================")
print("       LAMPORT LOGICAL CLOCK")
print("==================================")

print("Process Event Type Timestamp")
print("---------------------------------------")

#P1 performs local event E1
p1.local_event("E1")

#P1 sends message M1 to P2
m1 = p1.send_message("E2", p2, "M1")

#P2 receives message M1
p2.receive_message("E3", m1)

#receive timestamp for causal ordering
e3_timestamp = p2.events[-1][2]

#P2 performs local event E4
p2.local_event("E4")

#P2 sends message M2 to P3
m2 = p2.send_message("E5", p3, "M2")

#P1 performs local event E6
p1.local_event("E6")

#P1 sends message M3 to P3
m3 = p1.send_message("E7", p3, "M3")

#P3 receives message M2
p3.receive_message("E8", m2)

#receive timestamp for causal ordering
e8_timestamp = p3.events[-1][2]

#P3 receives message M3
p3.receive_message("E9", m3)
print("\n")

print("\n==================================")
print("     MESSAGE INFORMATION")
print("==================================")

print("Message Sender Receiver Timestamp")
print("---------------------------------------")

print(m1.message_id, m1.sender, m1.receiver, m1.timestamp)
print(m2.message_id, m2.sender, m2.receiver, m2.timestamp)
print(m3.message_id, m3.sender, m3.receiver, m3.timestamp)
print("\n")

#displaying the final logical clocks
print("\n==================================")
print("    FINAL LOGICAL CLOCKS")
print("==================================")

print("P1 =", p1.clock)
print("P2 =", p2.clock)
print("P3 =", p3.clock)
print("\n")

#causal ordering
print("\n==================================")
print("    CAUSAL RELATIONSHIPS")
print("==================================")
print("P1 SEND M1 --> P2 RECEIVE M1 |", m1.timestamp, "-->", e3_timestamp)
print("P2 SEND M2 --> P3 RECEIVE M2 |", m2.timestamp, "-->", e8_timestamp)
print("\n")

#concurrent events
p4 = Process("P4")
p5 = Process("P5")
print("\n==================================")
print("     CONCURRENT EVENTS")
print("==================================")
p4.local_event("E10")
p5.local_event("E11")