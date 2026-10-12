
class Process:
    def __init__(self, name, n):
        self.name = name
        self.vc = [0] * n

    def local(self):
        self.vc[processes.index(self)] += 1
        return self.vc.copy()

    def send(self, msg):
        self.vc[processes.index(self)] += 1
        print(f"{self.name} sends {msg}: {self.vc}")
        return self.vc.copy()

    def receive(self, msg):
        self.vc = [max(a, b) for a, b in zip(self.vc, msg)]
        self.vc[processes.index(self)] += 1
        return self.vc.copy()


def compare(a, b):
    if a == b:
        return "Same"
    if all(x <= y for x, y in zip(a, b)):
        return "A -> B"
    if all(x >= y for x, y in zip(a, b)):
        return "B -> A"
    return "Concurrent"


processes = [Process("P1", 3), Process("P2", 3), Process("P3", 3)]
p1, p2, p3 = processes
events = []

def show(p, event, kind, vc):
    events.append((p.name, event, kind, vc))
    print(f"{p.name}\t{event}\t{kind}\t{vc}")

print("PROCESS\tEVENT\tTYPE\tVECTOR CLOCK")
print("-" * 45)

show(p1, "E1", "LOCAL", p1.local())
m1 = p1.send("M1")
show(p1, "E2", "SEND", m1)
show(p2, "E3", "RECEIVE", p2.receive(m1))
show(p2, "E4", "LOCAL", p2.local())
m2 = p2.send("M2")
show(p2, "E5", "SEND", m2)
show(p1, "E6", "LOCAL", p1.local())
m3 = p1.send("M3")
show(p1, "E7", "SEND", m3)
show(p3, "E8", "RECEIVE", p3.receive(m2))
show(p3, "E9", "RECEIVE", p3.receive(m3))

print("\nEVENT RELATIONSHIPS")
print("EVENT A\tEVENT B\tRELATIONSHIP")
print("-" * 40)

for a, b in [(0, 1), (1, 2), (4, 7), (5, 3), (6, 4)]:
    print(f"{events[a][1]}\t{events[b][1]}\t{compare(events[a][3], events[b][3])}")
