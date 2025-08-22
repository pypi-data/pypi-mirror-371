"""
Main CLI Entry Point

Lightweight CLI entry point that uses the modular command system.
This replaces the monolithic cli.py with a clean, modular approach.
"""

import argparse
import os
import sys
from pathlib import Path

# Load environment variables from .env file and user credentials
from dotenv import load_dotenv

load_dotenv()  # Load from current directory
load_dotenv(Path.home() / ".stratequeue" / "credentials.env")  # Load user credentials

from .command_factory import create_command, get_supported_commands
from .utils import get_cli_logger, setup_logging
from .utils.color_formatter import (
    create_enhanced_help_epilog,
    format_help_header,
    format_welcome_message,
)
from .utils.command_help import get_command_help
from .utils.enhanced_parser import EnhancedArgumentParser

# Import command registry to ensure commands are registered
from . import command_registry  # noqa: F401

logger = get_cli_logger('main')


# Stub loading is now handled in test fixtures


def create_main_parser() -> argparse.ArgumentParser:
    """
    Create the main argument parser with subcommands

    Returns:
        Configured ArgumentParser
    """
    # Get supported commands for enhanced help
    supported_commands = get_supported_commands()

    parser = argparse.ArgumentParser(
        prog='stratequeue',
        description=format_help_header(),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=create_enhanced_help_epilog(supported_commands)
    )

    # Global arguments
    parser.add_argument(
        '--verbose', '-v',
        type=int,
        choices=[0, 1, 2],
        default=0,
        help='Verbosity level: 0=standard (warnings/errors only), 1=info, 2=debug (default: 0)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.0.1'
    )

    # Create subparsers for commands (hide the auto-generated list, show enhanced version in epilog)
    subparsers = parser.add_subparsers(
        dest='command',
        help=argparse.SUPPRESS,  # Hide the auto-generated command list
        metavar=''  # Remove "{command} ..." footer
    )

    # Register command parsers
    register_command_parsers(subparsers)

    return parser


def register_command_parsers(subparsers) -> None:
    """
    Register parsers for all available commands

    Args:
        subparsers: Subparsers object to add command parsers to
    """
    supported_commands = get_supported_commands()

    for command_name, _description in supported_commands.items():
        command = create_command(command_name)
        if command:
            # Create subparser for this command with aliases
            aliases = []
            if hasattr(command, 'aliases'):
                aliases_attr = command.aliases
                # Ensure aliases is a list
                if isinstance(aliases_attr, list):
                    aliases = aliases_attr
                elif aliases_attr is not None:
                    aliases = [aliases_attr] if isinstance(aliases_attr, str) else []

            # Get enhanced help content
            enhanced_help = get_command_help(command_name)

            # Hide individual command help since we show enhanced version in epilog
            # Use enhanced parser for individual command help
            subparser = subparsers.add_parser(
                command_name,
                aliases=aliases,
                help=argparse.SUPPRESS,  # Hide from auto-generated list
                description=enhanced_help['description'],
                epilog=enhanced_help['epilog'],
                formatter_class=EnhancedArgumentParser().formatter_class
            )

            # Let the command configure its parser
            command.setup_parser(subparser)





def show_welcome_message() -> None:
    """Show welcome message when no command is provided"""
    supported_commands = get_supported_commands()
    print(format_welcome_message(supported_commands))


def main(argv: list[str] | None = None) -> int:
    """
    Main CLI entry point

    Args:
        argv: Command line arguments (default: sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Test stubs are now handled in test fixtures
    
    try:
        # Parse arguments
        parser = create_main_parser()
        args = parser.parse_args(argv)

        # Setup logging
        setup_logging(verbose_level=args.verbose)
        logger.debug(f"CLI started with args: {args}")

        # Handle no command provided
        if not args.command:
            show_welcome_message()
            return 0

        # Get and execute command
        command = create_command(args.command)
        if not command:
            print(f"❌ Unknown command: {args.command}")
            print(f"💡 Available commands: {', '.join(get_supported_commands().keys())}")
            return 1

        # Execute command
        return command.run(args)

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 130  # Standard exit code for SIGINT

    except Exception as e:
        # In test environments, provide more detailed error information
        if os.getenv("SQ_TEST_STUB_BROKERS") == "1" or os.getenv("PYTEST_CURRENT_TEST"):
            import traceback
            print(f"❌ CLI Error in test environment: {e}", file=sys.stderr)
            print(f"❌ Full traceback:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        else:
            logger.exception(f"Unexpected error in main CLI: {e}")
            print(f"❌ Unexpected error: {e}")
            print("💡 Run with --verbose 1 or --verbose 2 for detailed error information")
        return 1


if __name__ == "__main__":
    sys.exit(main())
