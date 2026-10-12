
class process:
    def __init__(self, name):
        self.name = name
        self.c = 0

    def local_event(self, p, e):
        self.c = self.c + 1
        print(f"{p}       {e}         LOCAL       {self.c}")

    def send(self, receiver, message_val, e):
        self.c = self.c + 1

        message = {
            "message": message_val,
            "sender": self.name,
            "receiver": receiver.name,
            "timestamp": self.c
        }

        print(f"{self.name}       {e}         SEND        {self.c}")
        return message

    def receive(self, message, e):
        received_timestamp = message["timestamp"]

        self.c = max(self.c, received_timestamp) + 1
        print(f"{self.name}       {e}         RECEIVE     {self.c}")


P1 = process("P1")
P2 = process("P2")
P3 = process("P3")

print("LAMPORT LOGICAL CLOCK")
print("-----------------------------------------")
print("Process    Event    Type       Timestamp")
print("-----------------------------------------")

P1.local_event("P1", "E1")

message1 = P1.send(P2, "m1", "E2")

P2.receive(message1, "E3")

P2.local_event("P2", "E4")

message2 = P2.send(P3, "m2", "E5")

P1.local_event("P1", "E6")

message3 = P1.send(P3, "m3", "E7")

P3.receive(message2, "E8")

P3.receive(message3, "E9")

print("-----------------------------------------")
print()
print("Final Timestamps:")
print(f"P1: {P1.c}")
print(f"P2: {P2.c}")
print(f"P3: {P3.c}")

print("-----------------------------------------")
print()
print("Causal Relationships:")
print("E2 -> E3")
print("E3 -> E4")
print("E5 -> E8")
print("E7 -> E9")

print("-----------------------------------------")
print()
print("Concurrent Events:")
print("E6 and E8")
print("E6 and E5")
print("E6 and E4")
print("E6 and E3")
print("-----------------------------------------")
