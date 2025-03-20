# Socket Communication Project

This project demonstrates cross-language socket communication between Go and Python implementations using both TCP and UDP protocols.

## Directory Structure

- `go-implementation/`: Go implementation of servers and clients
- `python-implementation/`: Python implementation of servers and clients
- `samples/`: Contains sample DOT files for testing
- `test_*.sh`: Test scripts for different communication scenarios

## Building the Go Implementation

```bash
cd go-implementation
go build -o bin/tcp-server ./cmd/tcp/server
go build -o bin/tcp-client ./cmd/tcp/client
go build -o bin/udp-server ./cmd/udp/server
go build -o bin/udp-client ./cmd/udp/client
```

## Running the Tests

### Automated Test Suite

To run all tests automatically:

```bash
./test_all.sh
```

This will test all combinations of servers and clients:

- Go TCP Server with Python TCP Client
- Python TCP Server with Go TCP Client
- Go UDP Server with Python UDP Client
- Python UDP Server with Go UDP Client

### Individual Protocol Tests

For interactive testing of specific protocols:

```bash
# For TCP tests
./test_tcp.sh

# For UDP tests
./test_udp.sh
```

These scripts will prompt you to choose which server/client combination to test.

## Manual Testing

### TCP Communication

#### Go TCP Server

```bash
cd go-implementation
./bin/tcp-server -port 8080 -dir server_storage
```

#### Python TCP Client

```bash
cd python-implementation
python tcp/client.py -s localhost:8080 -d client_storage
```

### UDP Communication

#### Go UDP Server

```bash
cd go-implementation
./bin/udp-server -port 8081 -dir server_storage
```

#### Python UDP Client

```bash
cd python-implementation
python udp/client.py -s localhost:8081 -d client_storage
```

## Client Usage

Once any client is running, you can use the following commands:

- `send <file>` - Send a file to the server
- `exit` - Close the connection and exit

Example:

```
> send ../samples/test.dot
Sent 'test'
Saved 'test' locally
```

## Notes

- Clients and servers save received files in their respective storage directories
- All implementations use a common protocol for communication
- The simplified code focuses on the essentials of socket communication
