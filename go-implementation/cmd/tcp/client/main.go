package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"strings"

	"go-sockets/go-implementation/pkg/dot"
	"go-sockets/go-implementation/pkg/protocol"
)

var (
	serverAddr = flag.String("server", "localhost:8080", "Server address in format host:port")
	clientDir  = flag.String("dir", "client_storage", "Directory to store received DOT files")
	verbose    = flag.Bool("verbose", false, "Enable verbose logging")
)

func main() {
	flag.Parse()

	// Enable debug logging if verbose
	if *verbose {
		log.SetFlags(log.LstdFlags | log.Lmicroseconds)
		log.Println("Verbose mode enabled")
	} else {
		// Disable logging for non-verbose mode
		log.SetOutput(io.Discard)
	}

	// Create storage directory if it doesn't exist
	if err := os.MkdirAll(*clientDir, 0755); err != nil {
		log.Fatalf("Failed to create client storage directory: %v", err)
	}

	// Connect to server
	if *verbose {
		log.Printf("Connecting to server at %s...", *serverAddr)
	}
	
	conn, err := net.Dial("tcp", *serverAddr)
	if err != nil {
		log.Fatalf("Failed to connect to server: %v", err)
	}
	defer conn.Close()
	
	if *verbose {
		log.Printf("Connected to server %s from local address %s", conn.RemoteAddr(), conn.LocalAddr())
	}

	fmt.Println("Connected to server", *serverAddr)
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
			
			if *verbose {
				log.Printf("Loaded DOT file: %s\n", arg)
				log.Printf("DOT name: %s, content length: %d bytes\n", d.Name, len(d.Content))
			}

			// Send to server
			if *verbose {
				log.Printf("Sending DOT to server...")
			}
			
			if err := protocol.SendTCP(conn, d); err != nil {
				fmt.Printf("Error sending DOT to server: %v\n", err)
				continue
			}
			
			fmt.Printf("Sent DOT '%s' to server\n", d.Name)

			// Wait for acknowledgment
			if *verbose {
				log.Printf("Waiting for acknowledgment...")
			}
			
			ackDot, err := protocol.ReceiveTCP(conn)
			if err != nil {
				fmt.Printf("Error receiving acknowledgment: %v\n", err)
				continue
			}
			
			if *verbose {
				log.Printf("Received acknowledgment for DOT: %s\n", ackDot.Name)
			}

			// Save the acknowledged DOT locally
			if *verbose {
				log.Printf("Saving DOT to %s/%s.dot\n", *clientDir, ackDot.Name)
			}
			
			if err := ackDot.Save(*clientDir); err != nil {
				fmt.Printf("Error saving DOT locally: %v\n", err)
				continue
			}

			fmt.Printf("Received and saved DOT '%s' locally\n", ackDot.Name)
		
		default:
			fmt.Println("Unknown command. Use 'send <file>' or 'exit'")
		}
	}
} 