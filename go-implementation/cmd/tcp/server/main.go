package main

import (
	"flag"
	"fmt"
	"net"
	"os"
	"strings"

	"go-sockets/go-implementation/pkg/protocol"
)

var (
	port       = flag.Int("port", 8080, "Server port")
	storageDir = flag.String("dir", "server_storage", "Dir for files")
)

func handleClient(conn net.Conn, dir string) {
	defer conn.Close()
	addr := conn.RemoteAddr().String()
	fmt.Printf("New client: %s\n", addr)

	for {
		d, err := protocol.ReceiveTCP(conn)
		if err != nil {
			if err.Error() == "EOF" || strings.Contains(err.Error(), "connection reset by peer") {
				fmt.Printf("Client disconnected: %s\n", addr)
			}
			return
		}

		fmt.Printf("Got '%s' from %s\n", d.Name, addr)
		d.Save(dir)
		protocol.SendTCP(conn, d)
	}
}

func main() {
	flag.Parse()
	os.MkdirAll(*storageDir, 0755)

	addr := fmt.Sprintf(":%d", *port)
	listener, err := net.Listen("tcp", addr)
	if err != nil {
		fmt.Println("Listen error:", err)
		return
	}
	defer listener.Close()

	fmt.Printf("TCP Server on port %d, files in %s\n", *port, *storageDir)

	for {
		conn, err := listener.Accept()
		if err != nil {
			continue
		}
		go handleClient(conn, *storageDir)
	}
} 