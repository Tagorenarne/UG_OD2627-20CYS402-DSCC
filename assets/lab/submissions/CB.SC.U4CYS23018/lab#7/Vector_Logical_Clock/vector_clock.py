class Message:
    def __init__(self, message_id, sender, receiver, timestamp):
        self.message_id = message_id
        self.sender = sender
        self.receiver = receiver
        self.timestamp = timestamp.copy()

class Process:
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.clock = [0, 0, 0]
        self.events = []
        #events will store events in the process

    #local event, increment own component
    def local_event(self, event_name):
        self.clock[self.index] += 1

        self.events.append((event_name, "LOCAL", self.clock.copy()))
        print(f"{self.name} {event_name} LOCAL {self.clock}")

    #sending event, increment own component
    def send_message(self, event_name, receiver, message_id):
        self.clock[self.index] += 1

        #creating message with the updated vector timestamp
        message = Message(message_id, self.name, receiver.name, self.clock)

        self.events.append((event_name, "SEND", self.clock.copy()))
        print(f"{self.name} {event_name} SEND {self.clock}")
        return message

    #receiving event, take maximum and increment own component
    def receive_message(self, event_name, message):
        for i in range(len(self.clock)):
            self.clock[i] = max(self.clock[i], message.timestamp[i])

        self.clock[self.index] += 1

        self.events.append((event_name, "RECEIVE", self.clock.copy()))
        print(f"{self.name} {event_name} RECEIVE {self.clock}")

#comparing two vector timestamps
def compare_vectors(v1, v2):
    if v1 == v2:
        return "Same timestamp"

    if all(a <= b for a, b in zip(v1, v2)):
        return "V1 happened before V2"

    if all(a >= b for a, b in zip(v1, v2)):
        return "V2 happened before V1"

    return "Concurrent events"
