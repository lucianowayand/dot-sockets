#!/usr/bin/env python3
"""UDP server for DOT files."""

import os
import sys
import socket
import argparse
import glob
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import DOT, list_dots
from utils.protocol import Message, MAX_BUFFER_SIZE


def main():
    """Main function for the UDP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="UDP server for DOT files")
    parser.add_argument("-p", "--port", type=int, default=8081,
                        help="Server port (default: 8081)")
    parser.add_argument("-d", "--dir", type=str, default="server_storage",
                        help="Directory to store DOT files (default: server_storage)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    args = parser.parse_args()
    
    # Create storage directory if it doesn't exist
    os.makedirs(args.dir, exist_ok=True)
    
    # Load sample DOTs if storage is empty
    dots = list_dots(args.dir)
    if not dots:
        # Check for sample DOTs in the samples directory
        samples_dir = "../samples"
        for sample_path in glob.glob(os.path.join(samples_dir, "*.dot")):
            dot = DOT.load(sample_path)
            if dot and dot.save(args.dir):
                print(f"Loaded sample DOT: {dot.name}")
    
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind to port
        server_socket.bind(("0.0.0.0", args.port))
        print(f"UDP Server listening on port {args.port}")
        print(f"DOTs stored in {args.dir}")
        
        # Main loop
        while True:
            try:
                # Receive data directly
                print("Waiting for data...")
                buffer = bytearray(MAX_BUFFER_SIZE)
                n, client_address = server_socket.recvfrom_into(buffer)
                
                if args.verbose:
                    print(f"Received {n} bytes from {client_address}")
                
                # Parse message
                data = buffer[:n].decode('utf-8')
                if args.verbose:
                    print(f"Raw data: {data[:100]}...")
                    
                msg_dict = json.loads(data)
                if args.verbose:
                    print(f"Parsed message: {msg_dict.keys()}")
                    if 'dot' in msg_dict and msg_dict['dot']:
                        print(f"DOT data: {msg_dict['dot'].keys()}")
                
                # Extract DOT from message
                dot_data = msg_dict.get("dot")
                if not dot_data:
                    print("Error: No DOT data in message")
                    continue
                
                name = dot_data.get("name")
                if not name:
                    print("Warning: No name in DOT data, using 'unnamed'")
                    name = "unnamed"
                    
                content = dot_data.get("content")
                if not content:
                    print("Error: No content in DOT data")
                    continue
                
                dot = DOT(
                    name=name,
                    content=content
                )
                
                print(f"Received DOT '{dot.name}' from {client_address}")
                
                # Save the DOT to storage
                if not dot.save(args.dir):
                    print(f"Error saving DOT {dot.name}")
                    continue
                else:
                    print(f"Successfully saved DOT to {os.path.join(args.dir, dot.name + '.dot')}")
                
                # Create response message
                response = {
                    "type": "data",
                    "command": "acknowledge",
                    "name": dot.name,
                    "dot": {
                        "name": dot.name,
                        "content": dot.content
                    }
                }
                
                # Send acknowledgment back
                response_data = json.dumps(response).encode('utf-8')
                
                if args.verbose:
                    print(f"Sending response of {len(response_data)} bytes to {client_address}")
                    print(f"Response data: {response}")
                
                bytes_sent = server_socket.sendto(response_data, client_address)
                
                if args.verbose:
                    print(f"Sent {bytes_sent} bytes to {client_address}")
                
                print(f"Sent acknowledgment for DOT '{dot.name}' to {client_address}")
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                continue
            except Exception as e:
                print(f"Error processing message: {e}")
                import traceback
                traceback.print_exc()
                continue
                
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main() 