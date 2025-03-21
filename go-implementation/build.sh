#!/bin/bash

# Change to the go-implementation directory
cd "$(dirname "$0")"

# Create bin directory if it doesn't exist
mkdir -p bin

echo "Building TCP server..."
go build -o bin/tcp-server ./cmd/tcp/server

echo "Building TCP client..."
go build -o bin/tcp-client ./cmd/tcp/client

echo "Building UDP server..."
go build -o bin/udp-server ./cmd/udp/server

echo "Building UDP client..."
go build -o bin/udp-client ./cmd/udp/client

echo "Build completed! Binaries are in the bin/ directory."
echo ""
echo "To run the TCP server: ./bin/tcp-server -port 8080 -dir server_storage"
echo "To run the TCP client: ./bin/tcp-client -server localhost:8080 -dir client_storage"
echo "To run the UDP server: ./bin/udp-server -port 8081 -dir server_storage"
echo "To run the UDP client: ./bin/udp-client -server localhost:8081 -dir client_storage" 