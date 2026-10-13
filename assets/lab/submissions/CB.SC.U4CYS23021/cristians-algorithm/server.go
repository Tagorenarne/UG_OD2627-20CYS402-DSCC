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
	address := flag.String("address", ":8080", "address to listen on")
	flag.Parse()

	listener, err := net.Listen("tcp", *address)
	if err != nil {
		log.Fatal(err)
	}
	defer listener.Close()

	log.Printf("time server listening on %s", *address)
	for {
		connection, err := listener.Accept()
		if err != nil {
			log.Printf("accept connection: %v", err)
			continue
		}

		go handleConnection(connection)
	}
}

func handleConnection(connection net.Conn) {
	defer connection.Close()

	request, err := bufio.NewReader(connection).ReadString('\n')
	if err != nil {
		log.Printf("read request: %v", err)
		return
	}
	if strings.TrimSpace(request) != "TIME" {
		log.Printf("ignoring unknown request %q", strings.TrimSpace(request))
		return
	}

	serverTime := time.Now().UTC()
	fmt.Fprintf(connection, "%s\n", serverTime.Format(time.RFC3339Nano))
}
