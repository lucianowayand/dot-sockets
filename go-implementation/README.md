# Go Implementation of Socket Communication

This directory contains a simplified Go implementation for sending files over TCP and UDP sockets.

## Directory Structure

```
.
├── cmd/
│   ├── tcp/
│   │   ├── client/       # TCP client implementation
│   │   └── server/       # TCP server implementation
│   └── udp/
│       ├── client/       # UDP client implementation
│       └── server/       # UDP server implementation
├── pkg/
│   ├── dot/              # DOT file handling utilities
│   └── protocol/         # Protocol implementation for TCP/UDP
└── bin/                 # Compiled binaries
```

## Building

```bash
go build -o bin/tcp-server ./cmd/tcp/server
go build -o bin/tcp-client ./cmd/tcp/client
go build -o bin/udp-server ./cmd/udp/server
go build -o bin/udp-client ./cmd/udp/client
```

## Running

### TCP Server

```bash
./bin/tcp-server -port 8080 -dir server_storage
```

### TCP Client

```bash
./bin/tcp-client -server localhost:8080 -dir client_storage
```

### UDP Server

```bash
./bin/udp-server -port 8081 -dir server_storage
```

### UDP Client

```bash
./bin/udp-client -server localhost:8081 -dir client_storage
```

## Command Line Options

### Server Options

- `-port` - Server port (default: 8080 for TCP, 8081 for UDP)
- `-dir` - Directory to store files (default: server_storage)

### Client Options

- `-server` - Server address in format host:port (default: localhost:8080 for TCP, localhost:8081 for UDP)
- `-dir` - Directory to store received files (default: client_storage)

## Client Usage

Once the client is running, you can use the following commands:

- `send <file>` - Send a file to the server
- `exit` - Close the connection and exit

Example:

```
> send ../samples/test.dot
Sent 'test'
Saved 'test' locally
```

## Testing

For easier testing, use the scripts in the project root:

- `test_all.sh` - Automated testing of all combinations
- `test_tcp.sh` - Interactive TCP testing
- `test_udp.sh` - Interactive UDP testing
