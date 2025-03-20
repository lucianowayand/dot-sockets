#!/usr/bin/env python3
"""DOT file handling utilities for the Python implementation."""

import os
import json
from pathlib import Path


class DOT:
    """A class representing a DOT (Graph Description Language) document."""

    def __init__(self, name, content):
        """Initialize a DOT object with a name and content.

        Args:
            name (str): The name of the DOT file (without extension)
            content (str): The content of the DOT file
        """
        self.name = name
        self.content = content

    def save(self, directory):
        """Save the DOT to a file in the specified directory.

        Args:
            directory (str): The directory to save the DOT file in

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)

            filename = os.path.join(directory, f"{self.name}.dot")
            with open(filename, "w") as f:
                f.write(self.content)
            return True
        except Exception as e:
            print(f"Error saving DOT file: {e}")
            return False

    @classmethod
    def load(cls, path):
        """Load a DOT file from disk.

        Args:
            path (str): The path to the DOT file

        Returns:
            DOT: A DOT object if successful, None otherwise
        """
        try:
            with open(path, "r") as f:
                content = f.read()

            # Extract name from path (without extension)
            name = os.path.splitext(os.path.basename(path))[0]
            return cls(name, content)
        except Exception as e:
            print(f"Error loading DOT file: {e}")
            return None

    def to_dict(self):
        """Convert the DOT object to a dictionary.

        Returns:
            dict: A dictionary representation of the DOT object
        """
        return {
            "name": self.name,
            "content": self.content
        }

    @classmethod
    def from_dict(cls, data):
        """Create a DOT object from a dictionary.

        Args:
            data (dict): A dictionary with "name" and "content" keys

        Returns:
            DOT: A DOT object created from the dictionary
        """
        if not data or "name" not in data or "content" not in data:
            return None
        return cls(data["name"], data["content"])


def list_dots(directory):
    """List all DOT files in the specified directory.

    Args:
        directory (str): The directory to list DOT files from

    Returns:
        list: A list of DOT filenames (without path)
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # List files with .dot extension
        dot_files = []
        for file in os.listdir(directory):
            if file.endswith(".dot"):
                dot_files.append(file)
        return dot_files
    except Exception as e:
        print(f"Error listing DOT files: {e}")
        return [] 