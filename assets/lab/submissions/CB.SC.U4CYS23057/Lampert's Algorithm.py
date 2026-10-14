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

    def receive(self, time):
        self.clock = max(self.clock, time) + 1
        return self.clock


P1 = Process("P1")
P2 = Process("P2")
P3 = Process("P3")



print("\nProcess\tEvent\tType\t\ttime")


t1 = P1.local()
print(f"P1\tE1\tLOCAL\t\t{t1}")


m1 = P1.send()
print(f"P1\tE2\tSEND M1\t\t{m1}")


t3 = P2.receive(m1)
print(f"P2\tE3\tRECEIVE M1\t{t3}")


t4 = P2.local()
print(f"P2\tE4\tLOCAL\t\t{t4}")


m2 = P2.send()
print(f"P2\tE5\tSEND M2\t\t{m2}")


t6 = P1.local()
print(f"P1\tE6\tLOCAL\t\t{t6}")


m3 = P1.send()
print(f"P1\tE7\tSEND M3\t\t{m3}")


t8 = P3.receive(m2)
print(f"P3\tE8\tRECEIVE M2\t{t8}")


t9 = P3.receive(m3)
print(f"P3\tE9\tRECEIVE M3\t{t9}")



print("\nFinal Clocks:")
print("P1 =", P1.clock)
print("P2 =", P2.clock)
print("P3 =", P3.clock)

print("\nCausal Ordering:")
print("P1 SEND M1 -> P2 RECEIVE M1")
print(m1, "<", t3)

print("P2 SEND M2 -> P3 RECEIVE M2")
print(m2, "<", t8)

