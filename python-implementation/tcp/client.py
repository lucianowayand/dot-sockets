#!/usr/bin/env python3
"""TCP client for DOT files."""

import os
import sys
import socket
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import DOT, receive_tcp, send_tcp


def main():
    parser = argparse.ArgumentParser(description="TCP client")
    parser.add_argument("-s", "--server", default="localhost:8080")
    parser.add_argument("-d", "--dir", default="client_storage")
    args = parser.parse_args()
    
    os.makedirs(args.dir, exist_ok=True)
    
    host, port = args.server.split(":")
    port = int(port)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        print(f"Connecting to {host}:{port}...")
        client_socket.connect((host, port))
        print(f"Connected! Files: {args.dir}")
        print("\nCommands: send <file>, exit\n")
        
        while True:
            command = input("> ")
            if not command:
                continue
                
            if command == "exit":
                break
                
            parts = command.split(" ", 1)
            if len(parts) < 2:
                print("Invalid command")
                continue
                
            action, file_path = parts
            
            if action == "send":
                dot = DOT.load(file_path)
                if not dot:
                    print(f"Error loading: {file_path}")
                    continue
                    
                send_tcp(client_socket, dot)
                print(f"Sent '{dot.name}'")
                
                ack_dot = receive_tcp(client_socket)
                if not ack_dot:
                    print("No acknowledgment")
                    continue
                    
                ack_dot.save(args.dir)
                print(f"Saved '{ack_dot.name}' locally")
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