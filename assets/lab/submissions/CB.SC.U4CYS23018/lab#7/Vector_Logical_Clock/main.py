from vector_clock import Process, compare_vectors

#3 distributed processes
p1 = Process("P1", 0)
p2 = Process("P2", 1)
p3 = Process("P3", 2)

print("==================================")
print("       VECTOR CLOCK")
print("==================================")

print("Process Event Type Timestamp")
print("---------------------------------------")

#P1 performs local event E1
p1.local_event("E1")
e1_timestamp = p1.events[-1][2].copy()

#P1 sends message M1 to P2
m1 = p1.send_message("E2", p2, "M1")
e2_timestamp = p1.events[-1][2].copy()

#P2 receives message M1
p2.receive_message("E3", m1)
e3_timestamp = p2.events[-1][2].copy()

#P2 performs local event E4
p2.local_event("E4")
e4_timestamp = p2.events[-1][2].copy()

#P2 sends message M2 to P3
m2 = p2.send_message("E5", p3, "M2")
e5_timestamp = p2.events[-1][2].copy()

#P1 performs local event E6
p1.local_event("E6")
e6_timestamp = p1.events[-1][2].copy()

#P1 sends message M3 to P3
m3 = p1.send_message("E7", p3, "M3")
e7_timestamp = p1.events[-1][2].copy()

#P3 receives message M2
p3.receive_message("E8", m2)
e8_timestamp = p3.events[-1][2].copy()

#P3 receives message M3
p3.receive_message("E9", m3)
e9_timestamp = p3.events[-1][2].copy()

#displaying message information
print("\n==================================")
print("     MESSAGE INFORMATION")
print("==================================")

print("Message Sender Receiver Timestamp")
print("---------------------------------------")

print(m1.message_id, m1.sender, m1.receiver, m1.timestamp)
print(m2.message_id, m2.sender, m2.receiver, m2.timestamp)
print(m3.message_id, m3.sender, m3.receiver, m3.timestamp)

#displaying the final vector clocks
print("\n==================================")
print("    FINAL VECTOR CLOCKS")
print("==================================")

print("P1 =", p1.clock)
print("P2 =", p2.clock)
print("P3 =", p3.clock)

#causal ordering
print("\n==================================")
print("    CAUSAL RELATIONSHIPS")
print("==================================")

print("E2 --> E3:", compare_vectors(e2_timestamp, e3_timestamp))

print("E5 --> E8:", compare_vectors(e5_timestamp, e8_timestamp))

print("E8 --> E9:", compare_vectors(e8_timestamp, e9_timestamp))

#transitive causal ordering
print("\n==================================")
print("    TRANSITIVE CAUSALITY")
print("==================================")

print("E2 --> E3:", compare_vectors(e2_timestamp, e3_timestamp))

print("E3 --> E8:", compare_vectors(e3_timestamp, e8_timestamp))

print("E2 --> E8:", compare_vectors(e2_timestamp, e8_timestamp))

#comparing concurrent events
print("\n==================================")
print("     CONCURRENT EVENTS")
print("==================================")

print("E5 =", e5_timestamp)
print("E7 =", e7_timestamp)

print("Relationship: ", compare_vectors(e5_timestamp, e7_timestamp))
