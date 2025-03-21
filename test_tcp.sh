#!/bin/bash

# Simple TCP test script
echo "TCP Communication Test"
echo "======================"

# Create sample DOT file if not exists
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
kill_process() {
    pid=$(lsof -t -i:8080 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Killing process on port 8080"
        kill $pid 2>/dev/null
    fi
}

# Clean up on exit
trap kill_process EXIT

# Choose test mode
echo "Choose test mode:"
echo "1) Go Server, Python Client"
echo "2) Python Server, Go Client"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    # Go server, Python client
    echo "Starting Go TCP server..."
    cd go-implementation
    mkdir -p server_storage
    ./bin/tcp-server -port 8080 -dir server_storage &
    server_pid=$!
    cd ..
    
    echo "Press Enter when server is ready to start client..."
    read
    
    echo "Starting Python TCP client..."
    echo "Type 'send ../samples/test.dot' in the client and then 'exit'"
    cd python-implementation
    mkdir -p client_storage
    python tcp/client.py -s localhost:8080 -d client_storage
    
elif [ "$choice" == "2" ]; then
    # Python server, Go client
    echo "Starting Python TCP server..."
    cd python-implementation
    mkdir -p server_storage
    python tcp/server.py -p 8080 -d server_storage &
    server_pid=$!
    cd ..
    
    echo "Press Enter when server is ready to start client..."
    read
    
    echo "Starting Go TCP client..."
    echo "Type 'send ../samples/test.dot' in the client and then 'exit'"
    cd go-implementation
    mkdir -p client_storage
    ./bin/tcp-client -server localhost:8080 -dir client_storage
    
else
    echo "Invalid choice"
    exit 1
fi

# Check results
echo "Checking results..."
if [ "$choice" == "1" ]; then
    if [ -f "go-implementation/server_storage/test.dot" ] && [ -f "python-implementation/client_storage/test.dot" ]; then
        echo "Test passed: Files transferred successfully"
    else
        echo "Test failed: Files not transferred completely"
        echo "Server files:"
        ls -la go-implementation/server_storage/ 2>/dev/null || echo "Server directory not found"
        echo "Client files:"
        ls -la python-implementation/client_storage/ 2>/dev/null || echo "Client directory not found"
    fi
else
    if [ -f "python-implementation/server_storage/test.dot" ] && [ -f "go-implementation/client_storage/test.dot" ]; then
        echo "Test passed: Files transferred successfully"
    else
        echo "Test failed: Files not transferred completely"
        echo "Server files:"
        ls -la python-implementation/server_storage/ 2>/dev/null || echo "Server directory not found"
        echo "Client files:"
        ls -la go-implementation/client_storage/ 2>/dev/null || echo "Client directory not found"
    fi
fi 