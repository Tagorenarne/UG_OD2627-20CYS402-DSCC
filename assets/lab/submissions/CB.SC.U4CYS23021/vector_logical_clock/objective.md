1. Objective

Implement Vector Clock to track causal relationships between events in a distributed system and identify concurrent events.

The implementation must contain:

    At least 3 simulated distributed processes
    A vector clock maintained by each process
    Local events
    Inter-process message passing
    Send and receive events
    Vector timestamp calculation
    Causal ordering
    Detection of concurrent events
    Comparison of vector timestamps

Students may implement the experiment using any programming language of their choice.

    Note: Docker is not required for this experiment. The distributed processes may be simulated using functions, classes, objects, threads, or separate program instances.

2. Expected Architecture

The distributed system should contain at least three processes:

                 Distributed System

        +-----------------------+
        |       Process P1      |
        |    Vector Clock V1    |
        |                       |
        | Local / Send / Receive|
        +----------+------------+
                   |
                   | Message M1
                   | Vector: [2,0,0]
                   v
        +-----------------------+
        |       Process P2      |
        |    Vector Clock V2    |
        |                       |
        | Local / Send / Receive|
        +----------+------------+
                   |
                   | Message M2
                   | Vector: [2,3,0]
                   v
        +-----------------------+
        |       Process P3      |
        |    Vector Clock V3    |
        |                       |
        | Local / Send / Receive|
        +-----------------------+

For three processes:

P1 → [C1, C2, C3]
P2 → [C1, C2, C3]
P3 → [C1, C2, C3]

Initially:

P1 → [0,0,0]
P2 → [0,0,0]
P3 → [0,0,0]

Each position in the vector represents the knowledge of events at the corresponding process.
