c1 = 0
c2 = 0
c3 = 0

print("====================================================")
print("             LAMPORT LOGICAL CLOCK")
print("====================================================")
print("\n")
print("Process    Event    Type       Timestamp")
print("----------------------------------------------------")

c1 = c1 + 1
print("P1         E1       LOCAL      ", c1)

c1 = c1 + 1
msg_p1_p2 = c1
print("P1         E2       SEND       ", c1)

c2 = max(c2, msg_p1_p2) + 1
print("P2         E3       RECEIVE    ", c2)

c2 = c2 + 1
print("P2         E4       LOCAL      ", c2)

c2 = c2 + 1
msg_p2_p3 = c2
print("P2         E5       SEND       ", c2)

c1 = c1 + 1
print("P1         E6       LOCAL      ", c1)

c1 = c1 + 1
msg_p1_p3 = c1
print("P1         E7       SEND       ", c1)

c3 = max(c3, msg_p2_p3) + 1
print("P3         E8       RECEIVE    ", c3)

c3 = max(c3, msg_p1_p3) + 1
print("P3         E9       RECEIVE    ", c3)

print("----------------------------------------------------")
