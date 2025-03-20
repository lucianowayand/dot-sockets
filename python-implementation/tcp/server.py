#!/usr/bin/env python3
"""TCP server for DOT files."""

import os
import sys
import socket
import threading
import argparse
import glob
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import DOT, list_dots, receive_tcp, send_tcp


def handle_client(client_socket, client_address, storage_dir, verbose=False):
    """Handle a client connection.

    Args:
        client_socket (socket): The client socket
        client_address (tuple): The client address (host, port)
        storage_dir (str): Directory to store DOT files
        verbose (bool): Whether to enable verbose logging
    """
    print(f"New connection from {client_address}")
    
    try:
        while True:
            if verbose:
                print(f"Waiting for data from {client_address}...")
            
            # Receive DOT from client
            dot = receive_tcp(client_socket)
            if not dot:
                print(f"Client {client_address} disconnected")
                break
            
            print(f"Received DOT '{dot.name}' from {client_address}")
            
            # Save the DOT to storage
            if not dot.save(storage_dir):
                print(f"Error saving DOT {dot.name}")
                continue
            else:
                print(f"Successfully saved DOT to {os.path.join(storage_dir, dot.name + '.dot')}")
            
            if verbose:
                print(f"Sending acknowledgment to {client_address}")
                
            # Send acknowledgment back
            if not send_tcp(client_socket, dot):
                print(f"Error sending acknowledgment to {client_address}")
                break
                
            print(f"Sent acknowledgment for DOT '{dot.name}' to {client_address}")
    except ConnectionResetError:
        print(f"Connection reset by client {client_address}")
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
        if verbose:
            traceback.print_exc()
    finally:
        try:
            client_socket.close()
            print(f"Closed connection to {client_address}")
        except:
            pass


def main():
    """Main function for the TCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="TCP server for DOT files")
    parser.add_argument("-p", "--port", type=int, default=8080,
                        help="Server port (default: 8080)")
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
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind to port and start listening
        server_socket.bind(("0.0.0.0", args.port))
        server_socket.listen(5)
        print(f"TCP Server listening on port {args.port}")
        print(f"DOTs stored in {args.dir}")
        
        # Accept connections
        while True:
            client_socket, client_address = server_socket.accept()
            # Handle client in a new thread
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address, args.dir, args.verbose)
            )
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            traceback.print_exc()
    finally:
        server_socket.close()


if __name__ == "__main__":
    main() 