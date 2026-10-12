class Message:

    def __init__(self, msg_id, sender, receiver, timestamp):
        self.msg_id = msg_id
        self.sender = sender
        self.receiver = receiver
        self.timestamp = timestamp


class Process:

    def __init__(self, name):
        self.name = name
        self.clock = 0
        self.events = []


    def local_event(self, event_id):

        self.clock += 1

        self.events.append(
            (self.name, event_id, "LOCAL", self.clock)
        )

        print(
            f"{self.name} executes LOCAL event {event_id} "
            f"Timestamp = {self.clock}"
        )


    def send_message(self, event_id, receiver, msg_id):

        self.clock += 1

        message = Message(
            msg_id,
            self.name,
            receiver.name,
            self.clock
        )

        self.events.append(
            (self.name, event_id, "SEND", self.clock)
        )

        print(
            f"{self.name} sends {msg_id} to {receiver.name} "
            f"Timestamp = {self.clock}"
        )

        return message


    def receive_message(self, event_id, message):

        self.clock = max(
            self.clock,
            message.timestamp
        ) + 1


        self.events.append(
            (self.name, event_id, "RECEIVE", self.clock)
        )

        print(
            f"{self.name} receives {message.msg_id} from "
            f"{message.sender} Timestamp = {self.clock}"
        )



P1 = Process("P1")
P2 = Process("P2")
P3 = Process("P3")


print("\n======================================")
print("       LAMPORT LOGICAL CLOCK")
print("======================================\n")


P1.local_event("E1")


M1 = P1.send_message(
    "E2",
    P2,
    "M1"
)


P2.receive_message(
    "E3",
    M1
)


P2.local_event("E4")


M2 = P2.send_message(
    "E5",
    P3,
    "M2"
)


P1.local_event("E6")


M3 = P1.send_message(
    "E7",
    P3,
    "M3"
)


P3.receive_message(
    "E8",
    M2
)


P3.receive_message(
    "E9",
    M3
)



print("\n\n====================================================")
print("                 EVENT LOG")
print("====================================================")


print(
    f"{'Process':10}{'Event':10}{'Type':15}{'Timestamp'}"
)

print("-"*50)


all_events = (
    P1.events +
    P2.events +
    P3.events
)


for event in all_events:

    print(
        f"{event[0]:10}"
        f"{event[1]:10}"
        f"{event[2]:15}"
        f"{event[3]}"
    )



print("\n\n====================================================")
print("             CAUSAL ORDERING")
print("====================================================")


print(
"""
Event A              Event B
-------------------------------------------
P1 SEND M1  --->     P2 RECEIVE M1

P2 SEND M2  --->     P3 RECEIVE M2

Since SEND happens before RECEIVE:

Lamport(SEND) < Lamport(RECEIVE)
"""
)



print("\n====================================================")
print("          CONCURRENT EVENTS")
print("====================================================")


P4 = Process("P4")
P5 = Process("P5")


P4.local_event("C1")
P5.local_event("C2")


print(
"""
P4 Event C1 and P5 Event C2 are concurrent.

There is:
- No message exchange
- No causal relationship

Lamport timestamps alone cannot detect concurrency.
"""
)