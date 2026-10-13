package main

import (
	"bufio"
	"flag"
	"fmt"
	"log"
	"net"
	"strings"
	"time"
)

// Berkeley algorithm master. Each round it polls every slave for its clock,
// averages the slave offsets against its own clock (offset 0, the reference),
// and sends each slave the adjustment it must apply. RTT is ignored; this is
// the plain textbook algorithm, not Cristian's.
type slave struct {
	connection net.Conn
	channel    *bufio.ReadWriter
}

func (s *slave) send(message string) error {
	if _, err := fmt.Fprintln(s.channel, message); err != nil {
		return err
	}
	return s.channel.Flush()
}

func (s *slave) receive() (string, error) {
	line, err := s.channel.ReadString('\n')
	return strings.TrimSpace(line), err
}

func main() {
	address := flag.String("address", ":8080", "address to listen on")
	slaveCount := flag.Int("slaves", 3, "number of slaves to wait for")
	interval := flag.Duration("interval", 5*time.Second, "time between synchronization rounds")
	flag.Parse()

	listener, err := net.Listen("tcp", *address)
	if err != nil {
		log.Fatal(err)
	}
	defer listener.Close()
	log.Printf("master listening on %s, waiting for %d slaves", *address, *slaveCount)

	slaves := make([]*slave, 0, *slaveCount)
	for len(slaves) < *slaveCount {
		connection, err := listener.Accept()
		if err != nil {
			log.Printf("accept connection: %v", err)
			continue
		}
		slaves = append(slaves, &slave{
			connection: connection,
			channel:    bufio.NewReadWriter(bufio.NewReader(connection), bufio.NewWriter(connection)),
		})
		log.Printf("slave connected: %s (%d/%d)", connection.RemoteAddr(), len(slaves), *slaveCount)
	}

	masterOffset := time.Duration(0) // the master's own simulated skew
	for round := 1; ; round++ {
		offsets := []time.Duration{0} // master relative to itself, then slaves relative to the master
		for _, s := range slaves {
			if err := s.send("TIME?"); err != nil {
				log.Fatal(err)
			}
			reply, err := s.receive()
			if err != nil {
				log.Fatal(err)
			}
			slaveTime, err := time.Parse(time.RFC3339Nano, reply)
			if err != nil {
				log.Fatalf("parse slave time: %v", err)
			}
			offsets = append(offsets, slaveTime.Sub(time.Now().Add(masterOffset)))
		}

		var sum time.Duration
		for _, offset := range offsets {
			sum += offset
		}
		average := sum / time.Duration(len(offsets))

		adjustments := []time.Duration{average} // the master applies the full average to itself
		masterOffset += average
		for i, s := range slaves {
			adjustments = append(adjustments, average-offsets[i+1])
			if err := s.send("ADJUST " + adjustments[i+1].String()); err != nil {
				log.Fatal(err)
			}
		}

		log.Printf("round %d: offsets [master, slaves] %v, average %s, adjustments %v", round, offsets, average, adjustments)
		time.Sleep(*interval)
	}
}
