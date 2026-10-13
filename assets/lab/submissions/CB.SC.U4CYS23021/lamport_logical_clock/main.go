package main

import "fmt"

// Process models one participant in a distributed system. Each participant
// owns a separate Lamport logical clock.
type Process struct {
	name  string
	clock int
}

func (p *Process) local(event string) {
	p.clock++
	fmt.Printf("%s local event %-24s timestamp=%d\n", p.name, event, p.clock)
}

// send increments the sender's clock and returns the timestamp carried by the
// message.
func (p *Process) send(to *Process, message string) int {
	p.clock++
	fmt.Printf("%s sends %-24q to %s timestamp=%d\n", p.name, message, to.name, p.clock)
	return p.clock
}

// receive applies Lamport's rule: C = max(local clock, message timestamp) + 1.
func (p *Process) receive(from *Process, message string, timestamp int) {
	if p.clock < timestamp {
		p.clock = timestamp
	}
	p.clock++
	fmt.Printf("%s receives %-21q from %s timestamp=%d\n", p.name, message, from.name, p.clock)
}

func main() {
	p1 := &Process{name: "P1"}
	p2 := &Process{name: "P2"}
	p3 := &Process{name: "P3"}

	fmt.Println("Lamport Logical Clock Demonstration")
	fmt.Println("Initial clocks: P1=0, P2=0, P3=0")

	// These independent events have identical timestamps, so they are concurrent.
	p1.local("prepare report")
	p3.local("backup database")
	fmt.Println("P1:prepare report and P3:backup database are concurrent events.")

	timestamp := p1.send(p2, "report ready")
	p2.receive(p1, "report ready", timestamp)
	p2.local("review report")

	timestamp = p2.send(p3, "review complete")
	p3.receive(p2, "review complete", timestamp)
	p3.local("publish report")

	fmt.Printf("Final clocks: P1=%d, P2=%d, P3=%d\n", p1.clock, p2.clock, p3.clock)
	fmt.Println("Causal order: P1 send < P2 receive < P2 review < P2 send < P3 receive < P3 publish")
}
