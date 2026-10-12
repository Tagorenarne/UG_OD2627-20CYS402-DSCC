class Message:

    def __init__(self, msg_id, sender, receiver, vector):
        self.msg_id = msg_id
        self.sender = sender
        self.receiver = receiver
        self.vector = vector.copy()


class Process:

    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.vector_clock = [0, 0, 0]
        self.events = []


    def local_event(self, event):

        self.vector_clock[self.index] += 1

        self.events.append(
            [
                self.name,
                event,
                "LOCAL",
                self.vector_clock.copy()
            ]
        )

        print(
            f"{self.name} {event} LOCAL "
            f"Vector = {self.vector_clock}"
        )


    def send_message(self, event, receiver, msg_id):

        self.vector_clock[self.index] += 1

        message = Message(
            msg_id,
            self.name,
            receiver.name,
            self.vector_clock
        )

        self.events.append(
            [
                self.name,
                event,
                "SEND",
                self.vector_clock.copy()
            ]
        )

        print(
            f"{self.name} sends {msg_id} to {receiver.name} "
            f"Vector = {self.vector_clock}"
        )

        return message



    def receive_message(self, event, message):

        for i in range(3):
            self.vector_clock[i] = max(
                self.vector_clock[i],
                message.vector[i]
            )

        self.vector_clock[self.index] += 1


        self.events.append(
            [
                self.name,
                event,
                "RECEIVE",
                self.vector_clock.copy()
            ]
        )


        print(
            f"{self.name} receives {message.msg_id} "
            f"Vector = {self.vector_clock}"
        )



def compare_vectors(V1, V2):

    v1_less = False
    v2_less = False


    for i in range(3):

        if V1[i] < V2[i]:
            v1_less = True

        if V2[i] < V1[i]:
            v2_less = True


    if v1_less and not v2_less:
        return "V1 happened before V2"

    elif v2_less and not v1_less:
        return "V2 happened before V1"

    elif not v1_less and not v2_less:
        return "Same timestamp"

    else:
        return "Concurrent Events"



P1 = Process("P1",0)
P2 = Process("P2",1)
P3 = Process("P3",2)


print("="*60)
print("              VECTOR CLOCK")
print("="*60)



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



print("\n")
print("="*70)
print("EVENT LOG")
print("="*70)


print(
    f"{'Process':10}"
    f"{'Event':10}"
    f"{'Type':15}"
    f"Vector Timestamp"
)

print("-"*70)


all_events = (
    P1.events +
    P2.events +
    P3.events
)


for e in all_events:

    print(
        f"{e[0]:10}"
        f"{e[1]:10}"
        f"{e[2]:15}"
        f"{e[3]}"
    )



print("\n")
print("="*70)
print("CAUSAL ORDERING")
print("="*70)


print(
"""
P1 SEND M1  --->  P2 RECEIVE M1

P2 SEND M2  --->  P3 RECEIVE M2

Vector clocks prove that SEND happened before RECEIVE.
"""
)



print("="*70)
print("CONCURRENT EVENT DETECTION")
print("="*70)


A = [3,0,0]
B = [2,2,0]


print("Vector A =", A)
print("Vector B =", B)

print(
"Relationship:",
compare_vectors(A,B)
)