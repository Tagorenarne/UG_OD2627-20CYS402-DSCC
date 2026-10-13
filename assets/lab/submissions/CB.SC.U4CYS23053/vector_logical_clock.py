
class Process:
    def __init__(self, name, total):
        self.name = name
        self.clock = [0] * total

    def local_event(self):
        self.clock[process_list.index(self)] += 1
        return self.clock.copy()

    def send_message(self, message):
        self.clock[process_list.index(self)] += 1
        print(f"{self.name} sends {message}: {self.clock}")
        return self.clock.copy()

    def receive_message(self, timestamp):
        self.clock = [
            max(x, y) for x, y in zip(self.clock, timestamp)
        ]
        self.clock[process_list.index(self)] += 1
        return self.clock.copy()


def compare_clocks(clock_a, clock_b):
    if clock_a == clock_b:
        return "Same"
    if all(x <= y for x, y in zip(clock_a, clock_b)):
        return "A -> B"
    if all(x >= y for x, y in zip(clock_a, clock_b)):
        return "B -> A"
    return "Concurrent"


process_list = [
    Process("P1", 3),
    Process("P2", 3),
    Process("P3", 3)
]

p1, p2, p3 = process_list
event_list = []


def display(process, event, event_type, timestamp):
    event_list.append(
        (process.name, event, event_type, timestamp)
    )
    print(f"{process.name}\t{event}\t{event_type}\t{timestamp}")


print("PROCESS\tEVENT\tTYPE\tVECTOR CLOCK")
print("-" * 45)

display(p1, "E1", "LOCAL", p1.local_event())

msg1 = p1.send_message("M1")
display(p1, "E2", "SEND", msg1)

display(p2, "E3", "RECEIVE", p2.receive_message(msg1))
display(p2, "E4", "LOCAL", p2.local_event())

msg2 = p2.send_message("M2")
display(p2, "E5", "SEND", msg2)

display(p1, "E6", "LOCAL", p1.local_event())

msg3 = p1.send_message("M3")
display(p1, "E7", "SEND", msg3)

display(p3, "E8", "RECEIVE", p3.receive_message(msg2))
display(p3, "E9", "RECEIVE", p3.receive_message(msg3))

print("\nEVENT RELATIONSHIPS")
print("EVENT A\tEVENT B\tRELATIONSHIP")
print("-" * 40)

pairs = [(0, 1), (1, 2), (4, 7), (5, 3), (6, 4)]

for first, second in pairs:
    result = compare_clocks(
        event_list[first][3],
        event_list[second][3]
    )
    print(
        f"{event_list[first][1]}\t"
        f"{event_list[second][1]}\t{result}"
    )
