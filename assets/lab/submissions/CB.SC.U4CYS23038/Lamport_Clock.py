
class Process:
    def __init__(self, process_name):
        self.name = process_name
        self.logical_clock = 0


class Message:
    def __init__(self, message_id, sender_name, receiver_name, send_timestamp):
        self.message_id = message_id
        self.sender = sender_name
        self.receiver = receiver_name
        self.timestamp = send_timestamp

processes = {
    "P1": Process("P1"),
    "P2": Process("P2"),
    "P3": Process("P3")
}

event_log = []
total_events = 0
total_messages = 0

current_process = processes["P1"]

def perform_local_event(process):
    global total_events

    process.logical_clock += 1
    total_events += 1

    event_log.append(
        (total_events, process.name, "LOCAL", "-", process.logical_clock)
    )

    print("\nLOCAL EVENT")
    print(f"Event ID          : E{total_events}")
    print(f"Process           : {process.name}")
    print(f"Logical Clock     : {process.logical_clock}")


def send_message(sender_process, receiver_process):
    global total_events, total_messages, current_process

    sender_process.logical_clock += 1
    total_events += 1
    total_messages += 1

    send_event_id = total_events

    message = Message(
        f"M{total_messages}",
        sender_process.name,
        receiver_process.name,
        sender_process.logical_clock
    )

    event_log.append(
        (total_events, sender_process.name, "SEND",
         message.message_id, sender_process.logical_clock)
    )

    print("\nMESSAGE SENT")
    print(f"Message ID        : {message.message_id}")
    print(f"Sender            : {sender_process.name}")
    print(f"Receiver          : {receiver_process.name}")
    print(f"Send Event        : E{send_event_id}")
    print(f"Send Timestamp    : {message.timestamp}")

    receiver_process.logical_clock = max(
        receiver_process.logical_clock,
        message.timestamp
    ) + 1

    total_events += 1

    event_log.append(
        (total_events, receiver_process.name, "RECEIVE",
         message.message_id, receiver_process.logical_clock)
    )

    print(f"Receive Event     : E{total_events}")
    print(f"Receive Timestamp : {receiver_process.logical_clock}")

    current_process = receiver_process

def display_clocks():
    print("\nCURRENT LOGICAL CLOCKS")
    print("-" * 35)

    for process in processes.values():
        print(f"{process.name} = {process.logical_clock}")

    print(f"\nCurrent Process = {current_process.name}")

def display_event_log():
    if not event_log:
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

    for event_id, process_name, event_type, message_id, timestamp in event_log:
        print(
            f"{'E' + str(event_id):<8}"
            f"{process_name:<10}"
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
    print(f"{process.name} -> Logical Clock = {process.logical_clock}")

print(f"\nCurrent Process -> {current_process.name}")


while True:
    print("\n1. Local Event")
    print("2. Send Message")
    print("3. Show Clocks")
    print("4. Show Event Log")
    print("5. Exit")

    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        perform_local_event(current_process)

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

        receiver_process = processes[receiver_name]

        send_message(current_process, receiver_process)

    elif choice == "3":
        display_clocks()

    elif choice == "4":
        display_event_log()

    elif choice == "5":
        print("\nProgram terminated.")
        break

    else:
        print("Invalid choice!")
