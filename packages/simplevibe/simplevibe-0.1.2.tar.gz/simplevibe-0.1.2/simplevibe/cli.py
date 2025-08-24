"""
Command-line interface for simpleVibe.
"""

import argparse
import sys
from simplevibe.core import oddVibes, vibing, vibify
from simplevibe import get_backend_type
from simplevibe.api import llama3


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
    
    # vibify command
    vibify_parser = subparsers.add_parser("vibify", help="Enhance the vibes of text")
    vibify_parser.add_argument(
        "text", 
        type=str,
        help="The text to vibify"
    )
    
    # info command
    info_parser = subparsers.add_parser("info", help="Display information about simpleVibe")
    
    # set-backend command
    backend_parser = subparsers.add_parser("set-backend", help="Set the preferred inference backend")
    backend_parser.add_argument(
        "backend", 
        choices=["local", "remote"],
        help="The backend to use (local or remote)"
    )

    # llama3 command
    llama3_parser = subparsers.add_parser("llama3", help="Interact with the Llama3 API")
    llama3_parser.add_argument(
        "prompt",
        type=str,
        help="The prompt to send to the Llama3 API"
    )

    args = parser.parse_args()

    if not args.command:
        print(vibing())
        print(f"\nUsing {get_backend_type()} inference backend.")
        return 0
    
    if args.command == "oddVibes":
        result = oddVibes(args.number)
        print(f"Is {args.number} odd? {result}")
    elif args.command == "vibify":
        result = vibify(args.text)
        print(result)
    elif args.command == "info":
        print(f"simpleVibe - Using {get_backend_type()} inference backend")
        if get_backend_type() == 'local':
            print("Running with local inference using transformers and torch.")
        else:
            print("Running with remote inference using the API.")
        
        # Display environment variable info
        import os
        env_setting = os.environ.get('SIMPLEVIBE_BACKEND', 'not set')
        print(f"\nSIMPLEVIBE_BACKEND environment variable: {env_setting}")
        
    elif args.command == "set-backend":
        from simplevibe import set_backend
        success = set_backend(args.backend)
        if success:
            print(f"Backend preference set to: {args.backend}")
            print("This setting will persist for the current terminal session.")
    elif args.command == "llama3":
        from datetime import datetime
        import os
        system_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
        with open(system_prompt_path) as f:
            system_prompt = f.read()
        current_date = datetime.now().strftime("%Y-%m-%d")
        system_prompt = system_prompt.replace("{{currentDateTime}}", current_date)
        
        response = llama3(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": args.prompt},
            ],
            temperature=0.5,
            max_new_tokens=1000,
            top_p=0.9,
            top_k=40
        )
        print(response['output'])

    return 0


if __name__ == "__main__":
    sys.exit(main())
