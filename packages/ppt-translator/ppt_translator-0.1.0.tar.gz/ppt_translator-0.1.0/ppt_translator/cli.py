#!/usr/bin/env python3
"""
Command-line interface for PPT-Translator.

This module provides the main CLI entry point for the ppt-translator package.
"""

import sys
import os
from pathlib import Path


def main():
    """Main CLI entry point."""
    # Add the current directory to Python path to import modules
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))

    # Import and run the main server module
    try:
        from server import main as server_main

        server_main()
    except ImportError as e:
        print(f"Error importing server module: {e}")
        print("Please ensure all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running ppt-translator: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
