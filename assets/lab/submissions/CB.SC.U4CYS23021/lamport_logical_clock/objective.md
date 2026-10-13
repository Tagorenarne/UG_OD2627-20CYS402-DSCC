1. Objective

Implement Lamport's Logical Clock Algorithm to establish the logical ordering of events in a distributed system.

The implementation must contain:

    At least 3 simulated distributed processes
    Independent logical clocks for each process
    Local events
    Inter-process message passing
    Send and receive events
    Lamport timestamp calculation
    Causal ordering of events
    Demonstration of concurrent events

Students may implement the experiment using any programming language of their choice.

    Note: Docker is not required for this experiment. The distributed processes may be simulated using functions, classes, objects, threads, or separate program instances.

2. Expected Architecture

The distributed system should contain at least three processes:

                 Distributed System

        +-----------------------+
        |       Process P1      |
        |   Logical Clock: C1   |
        |                       |
        | Local / Send / Receive|
        +----------+------------+
                   |
                   | Message M1
                   v
        +-----------------------+
        |       Process P2      |
        |   Logical Clock: C2   |
        |                       |
        | Local / Send / Receive|
        +----------+------------+
                   |
                   | Message M2
                   v
        +-----------------------+
        |       Process P3      |
        |   Logical Clock: C3   |
        |                       |
        | Local / Send / Receive|
        +-----------------------+

Each process must maintain its own logical clock.

Initially:

P1 = 0
P2 = 0
P3 = 0
