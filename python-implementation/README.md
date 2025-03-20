# Python Implementation of Socket Communication

This directory contains a simplified Python implementation for sending files over TCP and UDP sockets.

## Directory Structure

```
.
├── tcp/                # TCP server and client
├── udp/                # UDP server and client
└── utils/              # Shared utilities
    ├── dot.py          # DOT file handling
    └── protocol.py     # Protocol implementation
```

## Requirements

Python 3.6 or later

## Running

### TCP Server

```bash
python tcp/server.py -p 8080 -d server_storage
```

### TCP Client

```bash
python tcp/client.py -s localhost:8080 -d client_storage
```

### UDP Server

```bash
python udp/server.py -p 8081 -d server_storage
```

### UDP Client

```bash
python udp/client.py -s localhost:8081 -d client_storage
```

## Command Line Options

### Server Options

- `-p, --port` - Server port (default: 8080 for TCP, 8081 for UDP)
- `-d, --dir` - Directory to store files (default: server_storage)

### Client Options

- `-s, --server` - Server address in format host:port (default: localhost:8080 for TCP, localhost:8081 for UDP)
- `-d, --dir` - Directory to store received files (default: client_storage)

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
