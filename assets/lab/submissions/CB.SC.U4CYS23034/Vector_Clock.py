import sys

vectors = {"P1": [0, 0, 0], "P2": [0, 0, 0], "P3": [0, 0, 0]}
positions = {"P1": 0, "P2": 1, "P3": 2}
events = []
message_count = 0


def record(process, kind, message="-"):
    event = (f"E{len(events) + 1}", process, kind, message, vectors[process].copy())
    events.append(event)
    print(f"{event[0]}  {process}  {kind:<8}  {message:<3}  {event[4]}")


def local_event(process):
    vectors[process][positions[process]] += 1
    record(process, "LOCAL")


def send_message(sender, receiver):
    global message_count
    vectors[sender][positions[sender]] += 1
    message_count += 1
    message = {"id": f"M{message_count}", "sender": sender,
               "receiver": receiver, "vector": vectors[sender].copy()}
    record(sender, "SEND", message["id"])
    return message


def receive_message(message):
    receiver = message["receiver"]
    for index in range(3):
        vectors[receiver][index] = max(vectors[receiver][index], message["vector"][index])
    vectors[receiver][positions[receiver]] += 1
    record(receiver, "RECEIVE", message["id"])


def compare_vectors(first, second):
    if first == second:
        return "equal"
    if all(first[i] <= second[i] for i in range(3)):
        return "happened before"
    if all(first[i] >= second[i] for i in range(3)):
        return "happened after"
    return "concurrent"


def show_events():
    print("\nEvent  Process  Type      Message  Vector")
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
    print("\nEvent comparisons")
    for first, second in ((0, 1), (1, 2), (1, 7), (4, 7), (5, 3), (6, 4)):
        relation = compare_vectors(events[first][4], events[second][4])
        print(f"{events[first][0]} / {events[second][0]}: {relation}")


def main():
    print("Vector clock - P1, P2, P3")
    while True:
        print("\n1. Local event\n2. Send message\n3. Show clocks\n4. Show events\n5. Exit")
        choice = input("Choice: ").strip()
        if choice in ("1", "2"):
            sender = input("Process (P1/P2/P3): ").strip().upper()
            if sender not in vectors:
                print("Invalid process")
                continue
            if choice == "1":
                local_event(sender)
            else:
                receiver = input("Send to: ").strip().upper()
                if receiver not in vectors or receiver == sender:
                    print("Choose another valid process")
                    continue
                receive_message(send_message(sender, receiver))
        elif choice == "3":
            print(vectors)
        elif choice == "4":
            show_events()
        elif choice == "5":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else main()
