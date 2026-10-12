class Process:
    def __init__(self, name, n, pos):
        self.name = name
        self.clock = [0] * n
        self.pos = pos

    def local(self, event):
        self.clock[self.pos] += 1
        print(self.name, event, "LOCAL", self.clock)

    def send(self, receiver, event):
        self.clock[self.pos] += 1

        msg = self.clock.copy()
        print(self.name, event, "SEND", self.clock)
        return msg

    def receive(self, msg, event):
        for i in range(len(self.clock)):
            self.clock[i] = max(self.clock[i], msg[i])

        self.clock[self.pos] += 1
        print(self.name, event, "RECEIVE", self.clock)


P1 = Process("P1", 3, 0)
P2 = Process("P2", 3, 1)
P3 = Process("P3", 3, 2)

print("VECTOR CLOCK SIMULATION")
print("-" * 10)

P1.local("E1")

m1 = P1.send(P2, "E2")
P2.receive(m1, "E3")

P2.local("E4")

m2 = P2.send(P3, "E5")

P1.local("E6")

m3 = P1.send(P3, "E7")

P3.receive(m2, "E8")
P3.receive(m3, "E9")

print("-" * 10)
print("FINAL VECTOR CLOCKS")
print("P1:", P1.clock)
print("P2:", P2.clock)
print("P3:", P3.clock)

print("-" * 10)
print("CAUSAL RELATIONSHIPS")
print("E2 -> E3")
print("E3 -> E4 -> E5")
print("E5 -> E8")
print("E7 -> E9")

print("-" * 10)
print("CONCURRENT EVENTS")
print("E5 and E6")
print("E6 and E8")
print("E4 and E6")
print("E3 and E6")

print("-" * 10)
print("VECTOR CLOCK ALGORITHM")