package main

import (
	"flag"
	"fmt"
	"net"
	"os"

	"go-sockets/go-implementation/pkg/protocol"
)

var (
	port       = flag.Int("port", 8081, "Server port")
	storageDir = flag.String("dir", "server_storage", "Dir for files")
)

func main() {
	flag.Parse()
	os.MkdirAll(*storageDir, 0755)

	addr := fmt.Sprintf(":%d", *port)
	serverAddr, err := net.ResolveUDPAddr("udp", addr)
	if err != nil {
		fmt.Println("Address error:", err)
		return
	}

	conn, err := net.ListenUDP("udp", serverAddr)
	if err != nil {
		fmt.Println("Listen error:", err)
		return
	}
	defer conn.Close()

	fmt.Printf("UDP Server on port %d, files in %s\n", *port, *storageDir)

	for {
		d, clientAddr, err := protocol.ReceiveUDP(conn)
		if err != nil {
			continue
		}

		fmt.Printf("Got '%s' from %s\n", d.Name, clientAddr)
		
		d.Save(*storageDir)
		protocol.SendUDP(conn, clientAddr, d)
	}
} 