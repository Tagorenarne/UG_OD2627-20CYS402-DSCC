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

// Berkeley algorithm slave. Runs a skewed clock (real time + -offset, a
// simulated drift so the demo has something to correct), answers TIME?
// with it, and applies the ADJUST deltas sent by the master.
func main() {
	address := flag.String("address", "server:8080", "master address")
	offset := flag.Duration("offset", 0, "simulated clock skew")
	flag.Parse()

	connection := dial(*address)
	defer connection.Close()
	log.Printf("slave up, master %s, clock skew %s", *address, *offset)

	channel := bufio.NewReadWriter(bufio.NewReader(connection), bufio.NewWriter(connection))
	for {
		line, err := channel.ReadString('\n')
		if err != nil {
			log.Fatal(err)
		}
		message := strings.TrimSpace(line)
		switch {
		case message == "TIME?":
			fmt.Fprintln(channel, time.Now().Add(*offset).UTC().Format(time.RFC3339Nano))
			channel.Flush()
		case strings.HasPrefix(message, "ADJUST "):
			delta, err := time.ParseDuration(strings.TrimPrefix(message, "ADJUST "))
			if err != nil {
				log.Fatalf("parse adjustment: %v", err)
			}
			*offset += delta
			log.Printf("adjusted by %s, clock skew now %s", delta, *offset)
		}
	}
}

// dial retries until the master is listening: the slave container usually
// starts before the master is ready to accept connections.
func dial(address string) net.Conn {
	for attempt := 0; ; attempt++ {
		connection, err := net.Dial("tcp", address)
		if err == nil {
			return connection
		}
		if attempt >= 30 {
			log.Fatalf("reach master at %s: %v", address, err)
		}
		time.Sleep(500 * time.Millisecond)
	}
}
