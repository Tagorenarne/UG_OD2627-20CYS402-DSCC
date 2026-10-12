"""Run: python demo.py"""

from cluster import Cluster


def show_cluster(cluster: Cluster, title: str) -> None:
    print(f"\n--- {title} ---")
    for node in cluster.nodes.values():
        print(
            f"Node {node.node_id}: alive={node.alive}, role={node.role}, term={node.current_term}, "
            f"log={[entry.command for entry in node.log]}, committed={node.commit_index}, "
            f"state_machine={node.state_machine}"
        )


def main() -> None:
    cluster = Cluster(3)
    cluster.tick(8)  # node 0 times out first and becomes leader
    leader = cluster.leader()
    assert leader is not None
    print(f"\nElected leader: node {leader.node_id}")

    leader.submit("SET time 10:00", cluster.time)
    cluster.tick(2)  # propagates the new commit index to followers
    show_cluster(cluster, "After first replicated command")

    old_leader_id = leader.node_id
    cluster.stop(old_leader_id)
    cluster.tick(12)  # a surviving node starts an election
    new_leader = cluster.leader()
    assert new_leader is not None
    print(f"\nNew leader after failure: node {new_leader.node_id}")
    new_leader.submit("SET time 10:30", cluster.time)
    cluster.tick(2)
    show_cluster(cluster, "After leader failure and second command")


if __name__ == "__main__":
    main()
