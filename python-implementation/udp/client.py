#!/usr/bin/env python3
"""UDP client for DOT files."""

import os
import sys
import socket
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import DOT, receive_udp, send_udp


def main():
    parser = argparse.ArgumentParser(description="UDP client")
    parser.add_argument("-s", "--server", default="localhost:8081")
    parser.add_argument("-d", "--dir", default="client_storage")
    parser.add_argument("-t", "--timeout", type=float, default=5.0)
    args = parser.parse_args()
    
    os.makedirs(args.dir, exist_ok=True)
    
    host, port = args.server.split(":")
    port = int(port)
    server_address = (host, port)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        print(f"UDP client ready, server: {args.server}, files: {args.dir}")
        print("\nCommands: send <file>, exit\n")
        
        while True:
            command = input("> ")
            if not command:
                continue
                
            if command == "exit":
                break
                
            parts = command.split(" ", 1)
            if len(parts) < 2:
                print("Invalid command. Use 'send <file>'")
                continue
                
            action, file_path = parts
            
            if action == "send":
                dot = DOT.load(file_path)
                if not dot:
                    print(f"Error loading: {file_path}")
                    continue
                
                send_udp(client_socket, server_address, dot)
                print(f"Sent '{dot.name}' to server")
                
                client_socket.settimeout(args.timeout)
                try:
                    ack_dot, server_addr = receive_udp(client_socket)
                    client_socket.settimeout(None)
                    
                    if not ack_dot:
                        print("No acknowledgment")
                        continue
                    
                    ack_dot.save(args.dir)
                    print(f"Saved '{ack_dot.name}' locally")
                    
                except socket.timeout:
                    print(f"No response in {args.timeout} seconds")
                    client_socket.settimeout(None)
                
            else:
                print("Unknown command")
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main() 