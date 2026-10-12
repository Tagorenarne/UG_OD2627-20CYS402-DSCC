class Process:
    def __init__(self, name):
        self.name = name
        self.clock = 0

    def local(self):
        self.clock += 1
        return self.clock

    def send(self):
        self.clock += 1
        return self.clock

    def receive(self, timestamp):
        self.clock = max(self.clock, timestamp) + 1
        return self.clock


P1 = Process("P1")
P2 = Process("P2")
P3 = Process("P3")


print("Process\tEvent\tType\tTimestamp")
print("----------------------------------------------")


t1 = P1.local()
print("P1\tE1\tLOCAL\t\t", t1)


t2 = P1.send()
M1 = t2
print("P1\tE2\tSEND M1\t\t", t2)


t3 = P2.receive(M1)
print("P2\tE3\tRECEIVE M1\t", t3)


t4 = P2.local()
print("P2\tE4\tLOCAL\t\t", t4)


t5 = P2.send()
M2 = t5
print("P2\tE5\tSEND M2\t\t", t5)


t6 = P1.local()
print("P1\tE6\tLOCAL\t\t", t6)


t7 = P1.send()
M3 = t7
print("P1\tE7\tSEND M3\t\t", t7)


t8 = P3.receive(M2)
print("P3\tE8\tRECEIVE M2\t", t8)


t9 = P3.receive(M3)
print("P3\tE9\tRECEIVE M3\t", t9)

print("----------------------------------------------")

print("\nFinal Clocks:")
print("P1 =", P1.clock)
print("P2 =", P2.clock)
print("P3 =", P3.clock)

print("\nCausal Ordering:")
print("P1 SEND M1 -> P2 RECEIVE M1 :", t2, "<", t3)
print("P2 SEND M2 -> P3 RECEIVE M2 :", t5, "<", t8)
