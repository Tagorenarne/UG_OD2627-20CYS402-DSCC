package main

import "fmt"

// Process owns one entry in a vector clock. Its index identifies that entry.
type Process struct {
	name  string
	index int
	clock []int
}

func (p *Process) local(event string) {
	p.clock[p.index]++
	fmt.Printf("%s local event %-24s timestamp=%v\n", p.name, event, p.clock)
}

// send increments the sender's entry and copies the vector into the message.
func (p *Process) send(to *Process, message string) []int {
	p.clock[p.index]++
	timestamp := append([]int(nil), p.clock...)
	fmt.Printf("%s sends %-24q to %s timestamp=%v\n", p.name, message, to.name, timestamp)
	return timestamp
}

// receive merges both vectors component-wise, then increments the receiver.
func (p *Process) receive(from *Process, message string, timestamp []int) {
	for index, value := range timestamp {
		if p.clock[index] < value {
			p.clock[index] = value
		}
	}
	p.clock[p.index]++
	fmt.Printf("%s receives %-21q from %s timestamp=%v\n", p.name, message, from.name, p.clock)
}

// compare reports the causal relation between two vector timestamps.
func compare(first, second []int) string {
	firstBefore := false
	secondBefore := false
	for index := range first {
		firstBefore = firstBefore || first[index] < second[index]
		secondBefore = secondBefore || second[index] < first[index]
	}
	switch {
	case firstBefore && !secondBefore:
		return "first happened before second"
	case secondBefore && !firstBefore:
		return "second happened before first"
	default:
		return "concurrent"
	}
}

func main() {
	p1 := &Process{name: "P1", index: 0, clock: []int{0, 0, 0}}
	p2 := &Process{name: "P2", index: 1, clock: []int{0, 0, 0}}
	p3 := &Process{name: "P3", index: 2, clock: []int{0, 0, 0}}

	fmt.Println("Vector Logical Clock Demonstration")
	fmt.Println("Initial clocks: P1=[0 0 0], P2=[0 0 0], P3=[0 0 0]")

	p1.local("prepare report")
	p1Event := append([]int(nil), p1.clock...)
	p3.local("backup database")
	p3Event := append([]int(nil), p3.clock...)
	fmt.Printf("Compare %v and %v: %s\n", p1Event, p3Event, compare(p1Event, p3Event))

	timestamp := p1.send(p2, "report ready")
	p2.receive(p1, "report ready", timestamp)
	p2.local("review report")

	timestamp = p2.send(p3, "review complete")
	p3.receive(p2, "review complete", timestamp)
	p3.local("publish report")

	fmt.Printf("Final clocks: P1=%v, P2=%v, P3=%v\n", p1.clock, p2.clock, p3.clock)
	fmt.Println("Causal order: P1 send < P2 receive < P2 review < P2 send < P3 receive < P3 publish")
}
