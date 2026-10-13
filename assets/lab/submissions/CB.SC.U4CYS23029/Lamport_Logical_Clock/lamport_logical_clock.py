
class Process:
    def __init__(self, process_name):
        self.name = process_name
        self.clock = 0

    def local_event(self):
        self.clock += 1
        return self.clock

    def send_message(self):
        self.clock += 1
        return self.clock

    def receive_message(self, message_timestamp):
        self.clock = max(self.clock, message_timestamp) + 1
        return self.clock


p1 = Process("P1")
p2 = Process("P2")
p3 = Process("P3")

print("Process\tEvent\tType\t\tTimestamp")
print("-" * 50)

time1 = p1.local_event()
print(f"P1\tE1\tLOCAL\t\t{time1}")

time2 = p1.send_message()
m1 = time2
print(f"P1\tE2\tSEND M1\t\t{time2}")

time3 = p2.receive_message(m1)
print(f"P2\tE3\tRECEIVE M1\t{time3}")

time4 = p2.local_event()
print(f"P2\tE4\tLOCAL\t\t{time4}")

time5 = p2.send_message()
m2 = time5
print(f"P2\tE5\tSEND M2\t\t{time5}")

time6 = p1.local_event()
print(f"P1\tE6\tLOCAL\t\t{time6}")

time7 = p1.send_message()
m3 = time7
print(f"P1\tE7\tSEND M3\t\t{time7}")

time8 = p3.receive_message(m2)
print(f"P3\tE8\tRECEIVE M2\t{time8}")

time9 = p3.receive_message(m3)
print(f"P3\tE9\tRECEIVE M3\t{time9}")

print("-" * 50)

print("\nFinal Clocks:")
print(f"P1 = {p1.clock}")
print(f"P2 = {p2.clock}")
print(f"P3 = {p3.clock}")

print("\nCausal Ordering:")
print(f"P1 SEND M1 -> P2 RECEIVE M1: {time2} < {time3}")
print(f"P2 SEND M2 -> P3 RECEIVE M2: {time5} < {time8}")