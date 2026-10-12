from enum import Enum
import threading
import time
import random
import requests

from config import OTHER_PEERS


class State(Enum):
    FOLLOWER = "Follower"
    CANDIDATE = "Candidate"
    LEADER = "Leader"


class Node:

    def __init__(self, node_id):

        self.id = node_id
        self.term = 0
        self.voted_for = None
        self.state = State.FOLLOWER

        self.log = []
        self.commit_index = 0

        self.last_heartbeat = time.time()

        self.start_election_timer()


    def start_election_timer(self):

        threading.Thread(
            target=self.election_timer,
            daemon=True
        ).start()


    def election_timer(self):

        while True:

            timeout = random.randint(5, 10)

            time.sleep(timeout)

            if self.state == State.LEADER:
                continue

            elapsed = time.time() - self.last_heartbeat

            if elapsed >= timeout:

                self.state = State.CANDIDATE
                self.term += 1

                print(
                    f"\n{self.id} became CANDIDATE (Term {self.term})",
                    flush=True
                )

                self.request_votes()


    def request_votes(self):

        votes = 1

        for peer, url in OTHER_PEERS.items():

            try:

                response = requests.post(
                    f"{url}/vote",
                    json={
                        "term": self.term,
                        "candidate": self.id
                    },
                    timeout=2
                )

                result = response.json()

                if result["voteGranted"]:

                    votes += 1

                    print(
                        f"{peer} voted for {self.id}",
                        flush=True
                    )

            except Exception:

                print(
                    f"{peer} unreachable",
                    flush=True
                )

        print(
            f"{self.id} has {votes} votes",
            flush=True
        )

        if votes >= 2:

            self.become_leader()


    def become_leader(self):

        if self.state == State.LEADER:
            return

        self.state = State.LEADER

        print(
            f"\n******** {self.id} became LEADER ********",
            flush=True
        )

        threading.Thread(
            target=self.heartbeat_loop,
            daemon=True
        ).start()


    def heartbeat_loop(self):

        while self.state == State.LEADER:

            self.send_heartbeats()

            time.sleep(1)


    def send_heartbeats(self):

        for peer, url in OTHER_PEERS.items():

            try:

                requests.post(
                    f"{url}/heartbeat",
                    json={
                        "leader": self.id,
                        "term": self.term
                    },
                    timeout=2
                )

            except Exception:

                pass


    def replicate_log(self, entry):

        acknowledgements = 1

        self.log.append(entry)

        print(
            f"{self.id} appended '{entry}'",
            flush=True
        )

        for peer, url in OTHER_PEERS.items():

            try:

                response = requests.post(
                    f"{url}/append",
                    json={
                        "leader": self.id,
                        "term": self.term,
                        "entry": entry
                    },
                    timeout=2
                )

                if response.json()["success"]:

                    acknowledgements += 1

            except Exception:

                pass

        print(
            f"Replication ACKs = {acknowledgements}",
            flush=True
        )

        if acknowledgements >= 2:

            self.commit_index += 1

            print(
                f"Committed entry #{self.commit_index}",
                flush=True
            )

            return True

        return False
