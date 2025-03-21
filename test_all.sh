#!/bin/bash

echo "============================================"
echo "Socket Communication Test Suite"
echo "============================================"

# Define colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create sample DOT file if not exists
echo "Checking for sample DOT file..."
SAMPLE_DIR="samples"
mkdir -p $SAMPLE_DIR
if [ ! -f "$SAMPLE_DIR/test.dot" ]; then
    echo "Creating sample DOT file..."
    echo "digraph G {
  A -> B;
  B -> C;
  C -> A;
}" > "$SAMPLE_DIR/test.dot"
fi

# Function to kill processes by port
kill_by_port() {
    pid=$(lsof -t -i:$1 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Killing process on port $1 (PID: $pid)"
        kill $pid 2>/dev/null
    fi
}

# Clean up on script exit
cleanup() {
    echo -e "${YELLOW}Cleaning up processes...${NC}"
    kill_by_port 8080
    kill_by_port 8081
    echo "Done."
}

trap cleanup EXIT

# Test TCP: Go Server, Python Client
test_tcp_go_server_python_client() {
    echo -e "${YELLOW}TEST: TCP - Go Server, Python Client${NC}"
    
    # Start Go TCP server
    echo "Starting Go TCP server..."
    cd go-implementation
    mkdir -p server_storage
    ./bin/tcp-server -port 8080 -dir server_storage &
    tcp_server_pid=$!
    cd ..
    sleep 2
    
    # Run Python TCP client
    echo "Running Python TCP client..."
    cd python-implementation
    mkdir -p client_storage
    python tcp/client.py -s localhost:8080 -d client_storage <<EOF
send ../samples/test.dot
exit
EOF
    cd ..
    
    # Kill server
    kill $tcp_server_pid 2>/dev/null
    sleep 1
    
    # Check results
    if [ -f "go-implementation/server_storage/test.dot" ] && [ -f "python-implementation/client_storage/test.dot" ]; then
        echo -e "${GREEN}✓ Test passed: Files transferred successfully${NC}"
    else
        echo -e "${RED}✗ Test failed: Files not transferred${NC}"
        echo "Server files:"
        ls -la go-implementation/server_storage/ 2>/dev/null || echo "Server directory not found"
        echo "Client files:"
        ls -la python-implementation/client_storage/ 2>/dev/null || echo "Client directory not found"
    fi
    
    # Clean up
    kill_by_port 8080
}

# Test TCP: Python Server, Go Client
test_tcp_python_server_go_client() {
    echo -e "${YELLOW}TEST: TCP - Python Server, Go Client${NC}"
    
    # Start Python TCP server
    echo "Starting Python TCP server..."
    cd python-implementation
    mkdir -p server_storage
    python tcp/server.py -p 8080 -d server_storage &
    tcp_server_pid=$!
    cd ..
    sleep 2
    
    # Run Go TCP client
    echo "Running Go TCP client..."
    cd go-implementation
    mkdir -p client_storage
    echo "send ../samples/test.dot" | ./bin/tcp-client -server localhost:8080 -dir client_storage
    cd ..
    
    # Kill server
    kill $tcp_server_pid 2>/dev/null
    sleep 1
    
    # Check results
    if [ -f "python-implementation/server_storage/test.dot" ] && [ -f "go-implementation/client_storage/test.dot" ]; then
        echo -e "${GREEN}✓ Test passed: Files transferred successfully${NC}"
    else
        echo -e "${RED}✗ Test failed: Files not transferred${NC}"
        echo "Server files:"
        ls -la python-implementation/server_storage/ 2>/dev/null || echo "Server directory not found"
        echo "Client files:"
        ls -la go-implementation/client_storage/ 2>/dev/null || echo "Client directory not found"
    fi
    
    # Clean up
    kill_by_port 8080
}

# Test UDP: Go Server, Python Client
test_udp_go_server_python_client() {
    echo -e "${YELLOW}TEST: UDP - Go Server, Python Client${NC}"
    
    # Start Go UDP server
    echo "Starting Go UDP server..."
    cd go-implementation
    mkdir -p server_storage
    ./bin/udp-server -port 8081 -dir server_storage &
    udp_server_pid=$!
    cd ..
    sleep 2
    
    # Run Python UDP client
    echo "Running Python UDP client..."
    cd python-implementation
    mkdir -p client_storage
    python udp/client.py -s localhost:8081 -d client_storage <<EOF
send ../samples/test.dot
exit
EOF
    cd ..
    
    # Kill server
    kill $udp_server_pid 2>/dev/null
    sleep 1
    
    # Check results
    if [ -f "go-implementation/server_storage/test.dot" ] && [ -f "python-implementation/client_storage/test.dot" ]; then
        echo -e "${GREEN}✓ Test passed: Files transferred successfully${NC}"
    else
        echo -e "${RED}✗ Test failed: Files not transferred${NC}"
        echo "Server files:"
        ls -la go-implementation/server_storage/ 2>/dev/null || echo "Server directory not found"
        echo "Client files:"
        ls -la python-implementation/client_storage/ 2>/dev/null || echo "Client directory not found"
    fi
    
    # Clean up
    kill_by_port 8081
}

# Test UDP: Python Server, Go Client
test_udp_python_server_go_client() {
    echo -e "${YELLOW}TEST: UDP - Python Server, Go Client${NC}"
    
    # Start Python UDP server
    echo "Starting Python UDP server..."
    cd python-implementation
    mkdir -p server_storage
    python udp/server.py -p 8081 -d server_storage &
    udp_server_pid=$!
    cd ..
    sleep 2
    
    # Run Go UDP client
    echo "Running Go UDP client..."
    cd go-implementation
    mkdir -p client_storage
    echo "send ../samples/test.dot" | ./bin/udp-client -server localhost:8081 -dir client_storage
    cd ..
    
    # Kill server
    kill $udp_server_pid 2>/dev/null
    sleep 1
    
    # Check results
    if [ -f "python-implementation/server_storage/test.dot" ] && [ -f "go-implementation/client_storage/test.dot" ]; then
        echo -e "${GREEN}✓ Test passed: Files transferred successfully${NC}"
    else
        echo -e "${RED}✗ Test failed: Files not transferred${NC}"
        echo "Server files:"
        ls -la python-implementation/server_storage/ 2>/dev/null || echo "Server directory not found"
        echo "Client files:"
        ls -la go-implementation/client_storage/ 2>/dev/null || echo "Client directory not found"
    fi
    
    # Clean up
    kill_by_port 8081
}

# Run all tests
echo -e "${GREEN}Running all tests...${NC}"
echo "============================================"

test_tcp_go_server_python_client

echo "============================================"

test_tcp_python_server_go_client

echo "============================================"

test_udp_go_server_python_client

echo "============================================"

test_udp_python_server_go_client

echo "============================================"
echo -e "${GREEN}All tests completed!${NC}" 