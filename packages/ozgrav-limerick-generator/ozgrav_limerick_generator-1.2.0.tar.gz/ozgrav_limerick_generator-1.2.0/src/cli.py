#!/usr/bin/env python3
"""
Command Line Interface for the Limerick Generator

This module provides a command-line interface for generating limericks using OpenAI's API.
"""

import argparse
import sys
from typing import Optional, List
from .limerick_generator import generate_limerick, SUPPORTED_MODELS, SUPPORTED_OUTPUT_FORMATS


def get_topic_from_stdin() -> str:
    """Read topic from stdin."""
    return sys.stdin.read().strip()


def get_topic_interactively() -> str:
    """Get topic from user input interactively."""
    try:
        return input("Enter a topic for your limerick: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        sys.exit(0)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate humorous limericks on any topic using OpenAI's API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  limerick "cats"                           # Generate a limerick about cats
  limerick cats dogs birds                  # Generate limericks about multiple topics
  echo "space travel" | limerick            # Read topic from stdin
  limerick --model gpt-4 "programming"      # Use GPT-4 model
  limerick -j "coffee"                      # Output in JSON format
  limerick --yaml "mountains"               # Output in YAML format
        """
    )
    
    # Topic argument - can be multiple topics or none (for stdin/interactive)
    parser.add_argument(
        'topics',
        nargs='*',
        help='Topic(s) for the limerick(s). If not provided, will read from stdin or prompt interactively.'
    )
    
    # API key argument
    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenAI API key. If not provided, will use OPENAI_API_KEY environment variable.'
    )
    
    # Model selection
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='gpt-3.5-turbo',
        choices=SUPPORTED_MODELS,
        help=f'OpenAI model to use (default: gpt-3.5-turbo). Choices: {", ".join(SUPPORTED_MODELS)}'
    )
    
    # Output format - mutually exclusive group
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output in JSON format'
    )
    output_group.add_argument(
        '--yaml', '-y',
        action='store_true',
        help='Output in YAML format'
    )
    
    return parser.parse_args()


def determine_output_format(args: argparse.Namespace) -> str:
    """Determine output format from command line arguments."""
    if args.json:
        return 'json'
    elif args.yaml:
        return 'yaml'
    else:
        return 'text'


def get_topics(args: argparse.Namespace) -> List[str]:
    """Get topics from arguments, stdin, or interactive input."""
    if args.topics:
        # Topics provided as command line arguments
        return args.topics
    elif not sys.stdin.isatty():
        # Reading from stdin (pipe or redirect)
        stdin_content = get_topic_from_stdin()
        if stdin_content:
            return [stdin_content]
        else:
            print("Error: No topic provided in stdin", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive mode
        topic = get_topic_interactively()
        if topic:
            return [topic]
        else:
            print("Error: No topic provided", file=sys.stderr)
            sys.exit(1)


def main():
    """Main CLI entry point."""
    try:
        args = parse_arguments()
        output_format = determine_output_format(args)
        topics = get_topics(args)
        
        # Generate limericks for each topic
        for topic in topics:
            try:
                limerick = generate_limerick(
                    topic=topic,
                    api_key=args.api_key,
                    model=args.model,
                    output=output_format
                )
                
                # Print topic header if multiple topics
                if len(topics) > 1:
                    print(f"\n--- Limerick about '{topic}' ---")
                
                print(limerick)
                
                # Add separator between limericks if multiple topics
                if len(topics) > 1 and topic != topics[-1]:
                    print()
                    
            except Exception as e:
                print(f"Error generating limerick for '{topic}': {e}", file=sys.stderr)
                if len(topics) == 1:
                    sys.exit(1)
                # Continue with other topics if multiple provided
                
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()