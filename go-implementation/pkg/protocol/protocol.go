package protocol

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net"

	"go-sockets/go-implementation/pkg/dot"
)

const (
	// MaxBufferSize is the maximum message size
	MaxBufferSize = 65535
)

// Message represents a protocol message
type Message struct {
	Type    string  `json:"type"`
	Command string  `json:"command"`
	Name    string  `json:"name"`
	DOT     *dot.DOT `json:"dot,omitempty"`
}

// SendTCP sends a DOT over a TCP connection
func SendTCP(conn net.Conn, d *dot.DOT) error {
	msg := Message{
		Type: "data",
		DOT:  d,
	}
	
	data, err := json.Marshal(msg)
	if err != nil {
		return fmt.Errorf("error marshaling message: %w", err)
	}
	
	// Display JSON for debugging
	log.Printf("Sending message: %s", string(data[:min(100, len(data))]))
	
	// Send the size as a header (4 bytes)
	size := len(data)
	sizeBytes := make([]byte, 4)
	sizeBytes[0] = byte(size >> 24)
	sizeBytes[1] = byte(size >> 16)
	sizeBytes[2] = byte(size >> 8)
	sizeBytes[3] = byte(size)
	
	log.Printf("Message size: %d bytes", size)
	
	if _, err := conn.Write(sizeBytes); err != nil {
		return fmt.Errorf("error sending message size: %w", err)
	}
	
	if _, err := conn.Write(data); err != nil {
		return fmt.Errorf("error sending message: %w", err)
	}
	
	return nil
}

// ReceiveTCP receives a DOT over a TCP connection
func ReceiveTCP(conn net.Conn) (*dot.DOT, error) {
	// Read the size header (4 bytes)
	sizeBytes := make([]byte, 4)
	n, err := io.ReadFull(conn, sizeBytes)
	if err != nil {
		if err == io.EOF {
			return nil, fmt.Errorf("connection closed while reading message size: %w", err)
		}
		return nil, fmt.Errorf("error reading message size: %w", err)
	}
	
	if n < 4 {
		return nil, fmt.Errorf("incomplete size header received: %d bytes", n)
	}
	
	size := int(sizeBytes[0])<<24 | int(sizeBytes[1])<<16 | int(sizeBytes[2])<<8 | int(sizeBytes[3])
	log.Printf("Receiving message of size: %d bytes", size)
	
	if size > MaxBufferSize {
		return nil, fmt.Errorf("message too large: %d bytes", size)
	}
	
	data := make([]byte, size)
	n, err = io.ReadFull(conn, data)
	if err != nil {
		if err == io.EOF {
			return nil, fmt.Errorf("connection closed while reading message data: %w", err)
		}
		return nil, fmt.Errorf("error reading message: %w", err)
	}
	
	if n < size {
		return nil, fmt.Errorf("incomplete message received: %d/%d bytes", n, size)
	}
	
	log.Printf("Received data: %s", string(data[:min(100, len(data))]))
	
	var msg Message
	if err := json.Unmarshal(data, &msg); err != nil {
		return nil, fmt.Errorf("error unmarshaling message: %w", err)
	}
	
	if msg.DOT == nil {
		return nil, fmt.Errorf("received message does not contain DOT data")
	}
	
	return msg.DOT, nil
}

// SendUDP sends a DOT over a UDP connection
func SendUDP(conn *net.UDPConn, addr *net.UDPAddr, d *dot.DOT) error {
	msg := Message{
		Type: "data",
		DOT:  d,
	}
	
	data, err := json.Marshal(msg)
	if err != nil {
		return fmt.Errorf("error marshaling message: %w", err)
	}
	
	if len(data) > MaxBufferSize {
		return fmt.Errorf("message too large for UDP: %d bytes", len(data))
	}
	
	_, err = conn.WriteToUDP(data, addr)
	if err != nil {
		return fmt.Errorf("error sending UDP message: %w", err)
	}
	
	return nil
}

// ReceiveUDP receives a DOT over a UDP connection
func ReceiveUDP(conn *net.UDPConn) (*dot.DOT, *net.UDPAddr, error) {
	buffer := make([]byte, MaxBufferSize)
	n, addr, err := conn.ReadFromUDP(buffer)
	if err != nil {
		return nil, nil, fmt.Errorf("error receiving UDP message: %w", err)
	}
	
	var msg Message
	if err := json.Unmarshal(buffer[:n], &msg); err != nil {
		return nil, addr, fmt.Errorf("error unmarshaling message: %w", err)
	}
	
	if msg.DOT == nil {
		return nil, addr, fmt.Errorf("received message does not contain DOT data")
	}
	
	return msg.DOT, addr, nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
} 