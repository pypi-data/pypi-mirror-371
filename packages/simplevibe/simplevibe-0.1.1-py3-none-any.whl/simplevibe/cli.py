"""
Command-line interface for simpleVibe.
"""

import argparse
import sys
from simplevibe.core import oddVibes, vibing


def main():
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(
        description="AI-powered operations with simpleVibe"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # oddVibes command
    odd_parser = subparsers.add_parser("oddVibes", help="Vibe check the oddness of a number")
    odd_parser.add_argument(
        "number", 
        type=str,
        help="The number to check"
    )
    
    args = parser.parse_args()

    if not args.command:
        print(vibing())
        return 0
    
    if args.command == "oddVibes":
        result = oddVibes(args.number)
        print(f"Is {args.number} odd? {result}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
