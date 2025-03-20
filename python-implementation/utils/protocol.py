#!/usr/bin/env python3
"""Protocol for sending and receiving DOT files over TCP/UDP."""

import json
import socket
import struct
from .dot import DOT

# Maximum buffer size for UDP
MAX_BUFFER_SIZE = 65535


class Message:
    """A message in the protocol."""

    def __init__(self, type_="data", command="", name="", dot=None):
        """Initialize a Message object.

        Args:
            type_ (str): The type of message
            command (str): Command to execute
            name (str): Name of the DOT file
            dot (DOT): The DOT object
        """
        self.type = type_
        self.command = command
        self.name = name
        self.dot = dot

    def to_dict(self):
        """Convert the Message to a dictionary.

        Returns:
            dict: A dictionary representation of the Message
        """
        result = {
            "type": self.type,
            "command": self.command,
            "name": self.name,
        }
        if self.dot:
            result["dot"] = self.dot.to_dict()
        return result

    @classmethod
    def from_dict(cls, data):
        """Create a Message from a dictionary.

        Args:
            data (dict): Dictionary containing message data

        Returns:
            Message: A Message object
        """
        msg = cls(
            type_=data.get("type", "data"),
            command=data.get("command", ""),
            name=data.get("name", ""),
        )
        if "dot" in data and data["dot"]:
            msg.dot = DOT.from_dict(data["dot"])
        return msg


def send_tcp(sock, dot):
    """Send a DOT over a TCP connection.

    Args:
        sock (socket): The socket to send over
        dot (DOT): The DOT object to send

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create message
        msg = Message(dot=dot)
        data = json.dumps(msg.to_dict()).encode("utf-8")

        # Send size header (4 bytes)
        size = len(data)
        size_bytes = struct.pack("!I", size)
        
        try:
            sock.sendall(size_bytes)
        except Exception as e:
            print(f"Error sending size header: {e}")
            return False

        # Send data
        try:
            sock.sendall(data)
        except Exception as e:
            print(f"Error sending data: {e}")
            return False
            
        return True
    except Exception as e:
        print(f"Error preparing message: {e}")
        import traceback
        traceback.print_exc()
        return False


def receive_tcp(sock):
    """Receive a DOT over a TCP connection.

    Args:
        sock (socket): The socket to receive from

    Returns:
        DOT: The received DOT object, or None on error
    """
    try:
        # Read size header (4 bytes)
        try:
            size_bytes = sock.recv(4)
            if not size_bytes:
                print("Connection closed by peer - no data received")
                return None
            if len(size_bytes) < 4:
                print(f"Incomplete size header received: {len(size_bytes)} bytes")
                return None
        except ConnectionResetError:
            print("Connection reset while reading size header")
            return None
        except Exception as e:
            print(f"Error reading size header: {e}")
            return None

        # Unpack size
        size = struct.unpack("!I", size_bytes)[0]
        print(f"Message size: {size} bytes")
        
        if size > MAX_BUFFER_SIZE:
            print(f"Message too large: {size} bytes")
            return None
        elif size == 0:
            print("Empty message received")
            return None

        # Read data
        data = b""
        remaining = size
        try:
            while remaining > 0:
                chunk = sock.recv(min(remaining, 4096))
                if not chunk:
                    print("Connection closed while reading data")
                    return None
                data += chunk
                remaining -= len(chunk)
        except Exception as e:
            print(f"Error reading data: {e}")
            return None

        # Parse message
        try:
            msg_dict = json.loads(data.decode("utf-8"))
            msg = Message.from_dict(msg_dict)
            if not msg.dot:
                print("Message does not contain a DOT object")
                return None
            return msg.dot
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw data: {data[:100]}...")
            return None
        except Exception as e:
            print(f"Error processing message: {e}")
            return None
            
    except Exception as e:
        print(f"Unexpected error receiving DOT: {e}")
        import traceback
        traceback.print_exc()
        return None


def send_udp(sock, address, dot):
    """Send a DOT over a UDP connection.

    Args:
        sock (socket): The socket to send over
        address (tuple): The (host, port) to send to
        dot (DOT): The DOT object to send

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create message
        msg = Message(dot=dot)
        data = json.dumps(msg.to_dict()).encode("utf-8")

        if len(data) > MAX_BUFFER_SIZE:
            print(f"Message too large for UDP: {len(data)} bytes")
            return False

        # Send data
        sock.sendto(data, address)
        return True
    except Exception as e:
        print(f"Error sending DOT: {e}")
        return False


def receive_udp(sock, buffer_size=MAX_BUFFER_SIZE):
    """Receive a DOT over a UDP connection.

    Args:
        sock (socket): The socket to receive from
        buffer_size (int): Maximum buffer size

    Returns:
        tuple: (DOT, address) tuple, or (None, address) on error
    """
    try:
        # Receive data
        data, address = sock.recvfrom(buffer_size)

        # Parse message
        msg_dict = json.loads(data.decode("utf-8"))
        msg = Message.from_dict(msg_dict)
        return msg.dot, address
    except Exception as e:
        print(f"Error receiving DOT: {e}")
        return None, None 