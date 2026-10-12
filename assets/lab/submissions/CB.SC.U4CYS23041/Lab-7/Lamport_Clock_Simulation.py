
class Process:
    def __init__(self, name):
        self.name = name
        self.clock = 0


class Message:
    def __init__(self, message_id, sender, receiver, timestamp):
        self.message_id = message_id
        self.sender = sender
        self.receiver = receiver
        self.timestamp = timestamp


processes = {
    "P1": Process("P1"),
    "P2": Process("P2"),
    "P3": Process("P3")
}

events = []
event_count = 0
message_count = 0

current_process = processes["P1"]


def local_event(process):
    global event_count

    process.clock += 1
    event_count += 1

    events.append(
        (event_count, process.name, "LOCAL", "-", process.clock)
    )

    print("\nLOCAL EVENT")
    print(f"Event ID          : E{event_count}")
    print(f"Process           : {process.name}")
    print(f"Lamport Timestamp : {process.clock}")


def send_message(sender, receiver):
    global event_count, message_count, current_process

    # Send event: increment sender's clock
    sender.clock += 1
    event_count += 1
    message_count += 1

    send_event_id = event_count
    message = Message(
        f"M{message_count}",
        sender.name,
        receiver.name,
        sender.clock
    )

    events.append(
        (event_count, sender.name, "SEND",
         message.message_id, sender.clock)
    )

    print("\nMESSAGE SENT")
    print(f"Message ID        : {message.message_id}")
    print(f"Sender            : {sender.name}")
    print(f"Receiver          : {receiver.name}")
    print(f"Send Event        : E{send_event_id}")
    print(f"Send Timestamp    : {message.timestamp}")

    # Receive event: Cj = max(Cj, message timestamp) + 1
    receiver.clock = max(
        receiver.clock,
        message.timestamp
    ) + 1

    event_count += 1

    events.append(
        (event_count, receiver.name, "RECEIVE",
         message.message_id, receiver.clock)
    )

    print(f"Receive Event     : E{event_count}")
    print(f"Receive Timestamp : {receiver.clock}")

    # Receiver becomes the current process
    current_process = receiver


def show_clocks():
    print("\nCURRENT LOGICAL CLOCKS")
    print("-" * 35)

    for process in processes.values():
        print(f"{process.name} = {process.clock}")

    print(f"\nCurrent Process = {current_process.name}")


def show_events():
    if not events:
        print("\nNo events recorded.")
        return

    print("\nEVENT LOG\n")

    print(
        f"{'Event':<8}"
        f"{'Process':<10}"
        f"{'Type':<12}"
        f"{'Message':<10}"
        f"{'Timestamp':<10}"
    )

    print("-" * 50)

    for number, process, event_type, message_id, timestamp in events:
        print(
            f"{'E' + str(number):<8}"
            f"{process:<10}"
            f"{event_type:<12}"
            f"{message_id:<10}"
            f"{timestamp:<10}"
        )

    print("-" * 50)


print("=" * 50)
print("       LAMPORT LOGICAL CLOCK SIMULATION")
print("=" * 50)

print("\nDistributed Processes:")
for process in processes.values():
    print(f"{process.name} -> Logical Clock = {process.clock}")

print(f"\nCurrent Process -> {current_process.name}")

while True:
    print("\n1. Local Event")
    print("2. Send Message")
    print("3. Show Clocks")
    print("4. Show Event Log")
    print("5. Exit")

    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        local_event(current_process)

    elif choice == "2":
        receiver_name = input(
            "Enter receiver process (P1/P2/P3): "
        ).strip().upper()

        if receiver_name not in processes:
            print("Invalid receiver process!")
            continue

        if receiver_name == current_process.name:
            print("Receiver cannot be the current process!")
            continue

        receiver = processes[receiver_name]
        send_message(current_process, receiver)

    elif choice == "3":
        show_clocks()

    elif choice == "4":
        show_events()

    elif choice == "5":
        print("\nProgram terminated.")
        break

    else:
        print("Invalid choice!")
