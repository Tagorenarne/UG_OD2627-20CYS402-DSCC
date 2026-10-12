import unittest

from cluster import Cluster


class RaftTests(unittest.TestCase):
    def test_elects_one_leader(self):
        cluster = Cluster(3)
        cluster.tick(8)
        self.assertIsNotNone(cluster.leader())

    def test_replicates_and_commits_command(self):
        cluster = Cluster(3)
        cluster.tick(8)
        leader = cluster.leader()
        assert leader is not None
        self.assertTrue(leader.submit("SET x 10", cluster.time))
        cluster.tick(2)
        self.assertTrue(all(node.state_machine == ["SET x 10"] for node in cluster.nodes.values()))

    def test_elects_new_leader_after_failure(self):
        cluster = Cluster(3)
        cluster.tick(8)
        old_leader = cluster.leader()
        assert old_leader is not None
        cluster.stop(old_leader.node_id)
        cluster.tick(12)
        new_leader = cluster.leader()
        self.assertIsNotNone(new_leader)
        self.assertNotEqual(new_leader.node_id, old_leader.node_id)


if __name__ == "__main__":
    unittest.main()
