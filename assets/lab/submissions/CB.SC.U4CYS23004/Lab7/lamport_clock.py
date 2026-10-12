class Process:
    def __init__(self, name):
        self.name = name
        self.clock = 0

    def local(self, event):
        self.clock += 1
        print(self.name, event, "LOCAL", self.clock)

    def send(self, event, msg, receiver):
        self.clock += 1
        print(self.name, event, "SEND", msg, "->", receiver.name, self.clock)
        return self.clock

    def receive(self, event, msg, sender_time, sender):
        self.clock = max(self.clock, sender_time) + 1
        print(self.name, event, "RECEIVE", msg, "<-", sender, self.clock)


p1 = Process("P1")
p2 = Process("P2")
p3 = Process("P3")

print("LAMPORT LOGICAL CLOCK")
print("---------------------")

print("Initial clocks:")
print("P1 =", p1.clock)
print("P2 =", p2.clock)
print("P3 =", p3.clock)

print("\nEvents:")
print("---------------------")

p1.local("E1")

m1_time = p1.send("E2", "M1", p2)

p2.receive("E3", "M1", m1_time, "P1")

p2.local("E4")

m2_time = p2.send("E5", "M2", p3)

p1.local("E6")

m3_time = p1.send("E7", "M3", p3)

p3.receive("E8", "M2", m2_time, "P2")

p3.receive("E9", "M3", m3_time, "P1")


print("\nCAUSAL ORDER")
print("---------------------")

print("P1 sends M1 at", m1_time)
print("P2 receives M1 at", m1_time + 1)

print("P2 sends M2 at", m2_time)
print("P3 receives M2 at", m2_time + 1)


print("\nCONCURRENT EVENTS")
print("---------------------")

p1.local("E10")
p2.local("E11")

print("\nE10 and E11 are concurrent.")
print("There is no message between P1 and P2 for these events.")