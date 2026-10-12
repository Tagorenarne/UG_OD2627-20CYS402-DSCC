class Process:
    def __init__(self, name, index, total_processes):
        self.name = name
        self.index = index
        self.clock = [0] * total_processes

    def local(self, event):
        self.clock[self.index] += 1
        print(self.name, event, "LOCAL", self.clock.copy())

    def send(self, event, msg, receiver):
        self.clock[self.index] += 1
        print(
            self.name, event, "SEND", msg,
            "->", receiver.name,
            self.clock.copy()
        )
        return self.clock.copy()

    def receive(self, event, msg, sender_clock, sender):
        # Merge sender's vector clock with receiver's clock
        for i in range(len(self.clock)):
            self.clock[i] = max(self.clock[i], sender_clock[i])

        # Increment receiver's own clock
        self.clock[self.index] += 1

        print(
            self.name, event, "RECEIVE", msg,
            "<-", sender,
            self.clock.copy()
        )


p1 = Process("P1", 0, 3)
p2 = Process("P2", 1, 3)
p3 = Process("P3", 2, 3)

print("VECTOR CLOCK")
print("---------------------")

print("Initial clocks:")
print("P1 =", p1.clock)
print("P2 =", p2.clock)
print("P3 =", p3.clock)

print("\nEvents:")
print("---------------------")

# P1: E1
p1.local("E1")

# P1 sends M1 to P2
m1_clock = p1.send("E2", "M1", p2)

# P2 receives M1
p2.receive("E3", "M1", m1_clock, "P1")

# P2: E4
p2.local("E4")

# P2 sends M2 to P3
m2_clock = p2.send("E5", "M2", p3)

# P1: E6
p1.local("E6")

# P1 sends M3 to P3
m3_clock = p1.send("E7", "M3", p3)

# P3 receives M2
p3.receive("E8", "M2", m2_clock, "P2")

# P3 receives M3
p3.receive("E9", "M3", m3_clock, "P1")


print("\nCAUSAL ORDER")
print("---------------------")

print("P1 sends M1 with vector clock", m1_clock)
print("P2 receives M1 with vector clock", p2.clock)

print("P2 sends M2 with vector clock", m2_clock)
print("P3 receives M2 before M3")


print("\nCONCURRENT EVENTS")
print("---------------------")

# Independent events
p1.local("E10")
p2.local("E11")

print("\nE10 and E11 are concurrent.")
print("There is no message between P1 and P2 for these events.")