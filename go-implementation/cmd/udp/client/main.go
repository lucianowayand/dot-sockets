package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"strings"
	"time"

	"go-sockets/go-implementation/pkg/dot"
	"go-sockets/go-implementation/pkg/protocol"
)

var (
	serverAddr = flag.String("server", "localhost:8081", "Server address in format host:port")
	clientDir  = flag.String("dir", "client_storage", "Directory to store received DOT files")
	timeout    = flag.Duration("timeout", 5*time.Second, "Timeout for server response")
	verbose    = flag.Bool("verbose", false, "Enable verbose output")
)

func main() {
	flag.Parse()

	// Create storage directory if it doesn't exist
	if err := os.MkdirAll(*clientDir, 0755); err != nil {
		log.Fatalf("Failed to create client storage directory: %v", err)
	}

	// Resolve server address
	host, portStr, err := net.SplitHostPort(*serverAddr)
	if err != nil {
		log.Fatalf("Invalid server address format: %v", err)
	}

	// If host is empty, use localhost
	if host == "" {
		host = "localhost"
	}

	// Parse port
	udpAddr, err := net.ResolveUDPAddr("udp", fmt.Sprintf("%s:%s", host, portStr))
	if err != nil {
		log.Fatalf("Failed to resolve server address: %v", err)
	}

	// Create UDP connection
	conn, err := net.DialUDP("udp", nil, udpAddr)
	if err != nil {
		log.Fatalf("Failed to connect to server: %v", err)
	}
	defer conn.Close()

	fmt.Println("Connected to UDP server", *serverAddr)
	fmt.Println("DOTs will be saved to", *clientDir)
	fmt.Println("\nCommands:")
	fmt.Println("  send <file>    - Send a DOT file to the server")
	fmt.Println("  exit           - Close the connection and exit")
	fmt.Println()

	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("> ")
		if !scanner.Scan() {
			break
		}

		command := scanner.Text()
		if command == "exit" {
			fmt.Println("Goodbye!")
			break
		}

		parts := strings.SplitN(command, " ", 2)
		if len(parts) < 2 {
			fmt.Println("Invalid command format. Use 'send <file>'")
			continue
		}

		action, arg := parts[0], parts[1]
		
		switch action {
		case "send":
			// Load DOT file
			d, err := dot.LoadDOT(arg)
			if err != nil {
				fmt.Printf("Error loading DOT file: %v\n", err)
				continue
			}

			// Create message
			msg := protocol.Message{
				Type: "data",
				DOT:  d,
			}
			
			data, err := json.Marshal(msg)
			if err != nil {
				fmt.Printf("Error marshaling message: %v\n", err)
				continue
			}
			
			if len(data) > protocol.MaxBufferSize {
				fmt.Printf("Message too large for UDP: %d bytes\n", len(data))
				continue
			}
			
			if *verbose {
				fmt.Printf("Sending %d bytes to %s\n", len(data), udpAddr.String())
			}
			
			// Send directly using Write since we have a connected socket
			n, err := conn.Write(data)
			if err != nil {
				fmt.Printf("Error sending DOT to server: %v\n", err)
				continue
			}
			
			if *verbose {
				fmt.Printf("Sent %d bytes\n", n)
			}
			
			fmt.Printf("Sent DOT '%s' to server\n", d.Name)

			// Set read deadline for timeout
			if err := conn.SetReadDeadline(time.Now().Add(*timeout)); err != nil {
				fmt.Printf("Error setting read deadline: %v\n", err)
				continue
			}

			// Wait for acknowledgment
			buffer := make([]byte, protocol.MaxBufferSize)
			
			// Use Read instead of ReadFromUDP for connected sockets
			n, err = conn.Read(buffer)
			if err != nil {
				if os.IsTimeout(err) {
					fmt.Println("Timeout waiting for server response")
				} else {
					fmt.Printf("Error receiving response: %v\n", err)
				}
				continue
			}
			
			if *verbose {
				fmt.Printf("Received %d bytes\n", n)
				fmt.Printf("Raw data: %s\n", string(buffer[:min(n, 100)]))
			}

			// Reset read deadline
			if err := conn.SetReadDeadline(time.Time{}); err != nil {
				fmt.Printf("Error resetting read deadline: %v\n", err)
			}

			// Process response
			var respMsg protocol.Message
			if err := json.Unmarshal(buffer[:n], &respMsg); err != nil {
				fmt.Printf("Error parsing response: %v\n", err)
				continue
			}
			
			if *verbose {
				fmt.Printf("Response message type: %s\n", respMsg.Type)
			}

			if respMsg.DOT == nil {
				fmt.Println("Received empty response from server")
				continue
			}

			// Save the acknowledged DOT locally
			if err := respMsg.DOT.Save(*clientDir); err != nil {
				fmt.Printf("Error saving DOT locally: %v\n", err)
				continue
			}

			fmt.Printf("Received and saved DOT '%s' from server\n", respMsg.DOT.Name)
		
		default:
			fmt.Println("Unknown command. Use 'send <file>' or 'exit'")
		}
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
} 