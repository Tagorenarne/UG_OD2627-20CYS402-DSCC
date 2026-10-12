class Message:
    def __init__(self, message_id, sender, receiver, timestamp):
        self.message_id = message_id
        self.sender = sender
        self.receiver = receiver
        self.timestamp = timestamp

class Process:
    def __init__(self, name):
        self.name = name
        self.clock = 0
        self.events = []
        #events will store events in the process

    #local event, C = C + 1
    def local_event(self, event_name):
        self.clock += 1

        self.events.append((event_name, "LOCAL", self.clock))
        print(f"{self.name} {event_name} {'LOCAL'} {self.clock}")

    #sending event, C = C + 1
    def send_message(self, event_name, receiver, message_id):
        self.clock += 1

        #creating message with the updated Lamport timestamp
        message = Message(message_id, self.name, receiver.name, self.clock)

        self.events.append((event_name, "SEND", self.clock))
        print(f"{self.name} {event_name} {'SEND'} {self.clock}")
        return message

    #receiving event, C = max(C, received timestamp) + 1
    def receive_message(self, event_name, message):
        self.clock = max(self.clock, message.timestamp) + 1

        self.events.append((event_name, "RECEIVE", self.clock))
        print(f"{self.name} {event_name} {'RECEIVE'} {self.clock}")
