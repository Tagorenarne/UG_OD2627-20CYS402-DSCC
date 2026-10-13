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

func main() {
	address := flag.String("address", "server:8080", "time server address")
	flag.Parse()

	connection, err := net.Dial("tcp", *address)
	if err != nil {
		log.Fatal(err)
	}
	defer connection.Close()

	requestTime := time.Now()
	if _, err := fmt.Fprintln(connection, "TIME"); err != nil {
		log.Fatal(err)
	}

	response, err := bufio.NewReader(connection).ReadString('\n')
	responseTime := time.Now()
	if err != nil {
		log.Fatal(err)
	}

	serverTime, err := time.Parse(time.RFC3339Nano, strings.TrimSpace(response))
	if err != nil {
		log.Fatalf("parse server time: %v", err)
	}

	roundTripTime := responseTime.Sub(requestTime)
	estimatedOffset := serverTime.Sub(requestTime) + roundTripTime/2
	synchronizedTime := time.Now().Add(estimatedOffset)

	fmt.Printf("client request time:  %s\n", requestTime.Format(time.RFC3339Nano))
	fmt.Printf("server time:         %s\n", serverTime.Format(time.RFC3339Nano))
	fmt.Printf("round-trip time:     %s\n", roundTripTime)
	fmt.Printf("estimated offset:    %s\n", estimatedOffset)
	fmt.Printf("synchronized time:   %s\n", synchronizedTime.Format(time.RFC3339Nano))
}
