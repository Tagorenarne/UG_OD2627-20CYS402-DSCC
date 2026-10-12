import sys

clocks = {"P1": 0, "P2": 0, "P3": 0}
events = []
message_count = 0


def record(process, kind, message="-"):
    event = (f"E{len(events) + 1}", process, kind, message, clocks[process])
    events.append(event)
    print(f"{event[0]}  {process}  {kind:<8}  {message:<3}  {event[4]}")


def local_event(process):
    clocks[process] += 1
    record(process, "LOCAL")


def send_message(sender, receiver):
    global message_count
    clocks[sender] += 1
    message_count += 1
    message = {"id": f"M{message_count}", "sender": sender,
               "receiver": receiver, "time": clocks[sender]}
    record(sender, "SEND", message["id"])
    return message


def receive_message(message):
    receiver = message["receiver"]
    clocks[receiver] = max(clocks[receiver], message["time"]) + 1
    record(receiver, "RECEIVE", message["id"])


def show_events():
    print("\nEvent  Process  Type      Message  Clock")
    for number, process, kind, message, timestamp in events:
        print(f"{number:<6} {process:<8} {kind:<9} {message:<8} {timestamp}")


def demo():
    local_event("P1")
    m1 = send_message("P1", "P2")
    receive_message(m1)
    local_event("P2")
    m2 = send_message("P2", "P3")
    local_event("P1")
    m3 = send_message("P1", "P3")
    receive_message(m2)
    receive_message(m3)
    show_events()
    print(f"\nM1: send time {events[1][4]} < receive time {events[2][4]}")
    print(f"M2: send time {events[4][4]} < receive time {events[7][4]}")
    print("E4 and E6 are concurrent in this sequence: neither causes the other.")
    print("Lamport timestamps alone cannot identify concurrency.")


def main():
    print("Lamport clock - P1, P2, P3")
    while True:
        print("\n1. Local event\n2. Send message\n3. Show clocks\n4. Show events\n5. Exit")
        choice = input("Choice: ").strip()
        if choice in ("1", "2"):
            sender = input("Process (P1/P2/P3): ").strip().upper()
            if sender not in clocks:
                print("Invalid process")
                continue
            if choice == "1":
                local_event(sender)
            else:
                receiver = input("Send to: ").strip().upper()
                if receiver not in clocks or receiver == sender:
                    print("Choose another valid process")
                    continue
                receive_message(send_message(sender, receiver))
        elif choice == "3":
            print(clocks)
        elif choice == "4":
            show_events()
        elif choice == "5":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else main()
