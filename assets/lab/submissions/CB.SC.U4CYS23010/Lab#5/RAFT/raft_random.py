import random
import time


class RaftNode:

    def __init__(self, node_id, cluster):
        self.node_id = node_id
        self.cluster = cluster

        # Initial Raft state
        self.state = "FOLLOWER"
        self.current_term = 0
        self.voted_for = None

        # Log and committed state
        self.log = []
        self.commit_index = -1
        self.state_machine = []

        # Leader information
        self.leader_id = None

        # Random election timeout
        self.reset_election_timeout()

    def reset_election_timeout(self):
        """
        Generate a random election timeout.
        """
        self.election_timeout = random.randint(5, 10)
        self.last_heartbeat = time.time()

    def receive_heartbeat(self, term, leader_id):
        """
        Receive a heartbeat from the leader.
        """

        if term >= self.current_term:

            self.current_term = term
            self.state = "FOLLOWER"
            self.leader_id = leader_id
            self.voted_for = None

            self.last_heartbeat = time.time()

            print(
                f"Node {self.node_id} received "
                f"a heartbeat from Node {leader_id}"
            )

    def request_vote(self, candidate_id, candidate_term):
        """
        Process a vote request from a candidate.
        """

        if candidate_term < self.current_term:
            return False

        if candidate_term > self.current_term:

            self.current_term = candidate_term
            self.voted_for = None
            self.state = "FOLLOWER"

        if (
            self.voted_for is None
            or self.voted_for == candidate_id
        ):

            self.voted_for = candidate_id

            print(
                f"Node {self.node_id} voted "
                f"for Node {candidate_id}"
            )

            return True

        return False

    def start_election(self):
        """
        Become a candidate and request votes.
        """

        self.state = "CANDIDATE"

        self.current_term += 1


        self.voted_for = self.node_id

        votes = 1

        print("\n" + "=" * 55)

        print(
            f"Node {self.node_id} started "
            f"an election for Term {self.current_term}"
        )

        print(
            f"Node {self.node_id} voted for itself"
        )

        for node in self.cluster:

            if node.node_id != self.node_id:

                vote_granted = node.request_vote(
                    self.node_id,
                    self.current_term
                )

                if vote_granted:
                    votes += 1

        majority = len(self.cluster) // 2 + 1

        print(
            f"\nNode {self.node_id} received "
            f"{votes} vote(s)"
        )

        print(
            f"Votes required for majority: {majority}"
        )

        if votes >= majority:

            self.become_leader()

        else:

            print(
                f"\nNode {self.node_id} failed "
                f"to become leader"
            )

            self.state = "FOLLOWER"

    def become_leader(self):
        """
        Change the candidate state to leader.
        """

        self.state = "LEADER"

        self.leader_id = self.node_id

        print(
            f"\nNode {self.node_id} became "
            f"the LEADER for Term {self.current_term}"
        )

        print("=" * 55)

        self.send_heartbeats()

    def send_heartbeats(self):
        """
        Send heartbeats to all followers.
        """

        if self.state != "LEADER":
            return

        print(
            f"\nLeader Node {self.node_id} "
            f"is sending heartbeats..."
        )

        for node in self.cluster:

            if node.node_id != self.node_id:

                node.receive_heartbeat(
                    self.current_term,
                    self.node_id
                )

    def add_client_command(self, command):
        """
        Add a client command and replicate it
        to all followers.
        """

        if self.state != "LEADER":

            print(
                f"Node {self.node_id} is not "
                f"the leader."
            )

            return

        log_entry = {
            "term": self.current_term,
            "command": command
        }

        self.log.append(log_entry)

        log_index = len(self.log) - 1

        print(
            f"\nLeader Node {self.node_id} "
            f"received command:"
        )

        print(f"  {command}")

        print(
            f"Command added at "
            f"log index {log_index}"
        )

        acknowledgments = 1

        for node in self.cluster:

            if node.node_id != self.node_id:

                success = node.receive_log_entry(
                    log_entry,
                    log_index,
                    self.current_term,
                    self.node_id
                )

                if success:
                    acknowledgments += 1

        majority = len(self.cluster) // 2 + 1

        if acknowledgments >= majority:

            self.commit_index = log_index

            self.apply_entry(log_entry)

            print(
                f"\nCommand committed with "
                f"{acknowledgments} "
                f"acknowledgment(s)"
            )

            for node in self.cluster:

                if node.node_id != self.node_id:

                    node.commit_entry(
                        log_index
                    )

        else:

            print(
                "\nCommand could not "
                "be committed"
            )

    def receive_log_entry(
        self,
        entry,
        log_index,
        term,
        leader_id
    ):
        """
        Receive and store a log entry
        from the leader.
        """

        if term < self.current_term:
            return False

        self.current_term = term
        self.state = "FOLLOWER"
        self.leader_id = leader_id

        if len(self.log) == log_index:

            self.log.append(entry)

        elif len(self.log) > log_index:

            self.log[log_index] = entry

        else:

            return False

        print(
            f"Node {self.node_id} replicated "
            f"the command:"
        )

        print(
            f"  {entry['command']}"
        )

        return True

    def commit_entry(self, log_index):
        """
        Commit a replicated log entry.
        """

        if log_index < len(self.log):

            self.commit_index = log_index

            entry = self.log[log_index]

            self.apply_entry(entry)

            print(
                f"Node {self.node_id} "
                f"committed the command"
            )

    def apply_entry(self, entry):
        """
        Apply a committed entry to the
        node's state machine.
        """

        if entry not in self.state_machine:

            self.state_machine.append(entry)

    def display_status(self):
        """
        Display the final status of a node.
        """

        print("\n" + "-" * 55)

        print(f"Node ID       : {self.node_id}")

        print(f"State         : {self.state}")

        print(
            f"Current Term  : "
            f"{self.current_term}"
        )

        print(
            f"Leader ID     : "
            f"{self.leader_id}"
        )

        print(f"Log           : {self.log}")

        print(
            f"Commit Index  : "
            f"{self.commit_index}"
        )

        print(
            f"State Machine : "
            f"{self.state_machine}"
        )

        print("-" * 55)


def main():

    print("\nRAFT CONSENSUS ALGORITHM SIMULATION")

    print("=" * 55)

    cluster = []

    # Create five Raft nodes
    for node_id in range(1, 6):

        node = RaftNode(
            node_id,
            cluster
        )

        cluster.append(node)

    print("\nFive Raft nodes were created")

    print("\nRandom election timeouts:")

    for node in cluster:

        print(
            f"Node {node.node_id}: "
            f"{node.election_timeout} seconds"
        )

    candidate = random.choice(cluster)

    print(
        f"\nNode {candidate.node_id} "
        f"was randomly selected "
        f"to start the election"
    )

    candidate.start_election()

    leader = None

    for node in cluster:

        if node.state == "LEADER":

            leader = node

            break

    if leader is not None:

        leader.add_client_command(
            "SET temperature = 25"
        )

        leader.add_client_command(
            "SET humidity = 60"
        )

        leader.send_heartbeats()

    else:

        print(
            "\nNo leader was elected"
        )

    print("\nFINAL CLUSTER STATUS")

    for node in cluster:

        node.display_status()


if __name__ == "__main__":

    main()
