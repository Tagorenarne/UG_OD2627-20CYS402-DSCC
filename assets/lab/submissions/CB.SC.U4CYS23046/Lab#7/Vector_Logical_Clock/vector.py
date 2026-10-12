p1 = [0, 0, 0]
p2 = [0, 0, 0]
p3 = [0, 0, 0]

print("=" * 60)
print("                  VECTOR CLOCK")
print("=" * 60)
print()
print("Process    Event    Type        Vector Timestamp")
print("-" * 60)

p1[0] += 1
print("P1         E1       LOCAL       ", p1)

p1[0] += 1
msg_p1_p2 = p1.copy()
print("P1         E2       SEND        ", p1)

for i in range(3):
    p2[i] = max(p2[i], msg_p1_p2[i])
p2[1] += 1
print("P2         E3       RECEIVE     ", p2)

p2[1] += 1
print("P2         E4       LOCAL       ", p2)

p2[1] += 1
msg_p2_p3 = p2.copy()
print("P2         E5       SEND        ", p2)

p1[0] += 1
print("P1         E6       LOCAL       ", p1)

p1[0] += 1
msg_p1_p3 = p1.copy()
print("P1         E7       SEND        ", p1)

for i in range(3):
    p3[i] = max(p3[i], msg_p2_p3[i])
p3[2] += 1
print("P3         E8       RECEIVE     ", p3)

for i in range(3):
    p3[i] = max(p3[i], msg_p1_p3[i])
p3[2] += 1
print("P3         E9       RECEIVE     ", p3)

print("-" * 60)
