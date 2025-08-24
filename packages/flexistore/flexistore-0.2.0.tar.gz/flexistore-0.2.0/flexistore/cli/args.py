"""CLI argument parsing for FlexiStore."""

import argparse
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="FlexiStore interactive CLI",
        prog="flexistore",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  flexistore --provider azure          # Use Azure Blob Storage
  flexistore --provider aws            # Use AWS S3
  flexistore --no-verify-ssl           # Disable SSL verification
        """
    )

    parser.add_argument(
        "--provider",
        choices=["azure", "aws"],
        help="Storage provider to use (default: value of FLEXISTORE_PROVIDER or azure)",
    )

    ssl_group = parser.add_mutually_exclusive_group()
    ssl_group.add_argument(
        "--no-verify-ssl",
        action="store_false",
        dest="verify_ssl",
        help="Disable SSL certificate verification for AWS (default: enabled)",
    )
    ssl_group.add_argument(
        "--verify-ssl",
        action="store_true",
        dest="verify_ssl",
        help="Enable SSL certificate verification for AWS (default)",
    )
    parser.set_defaults(verify_ssl=False)

    parser.add_argument(
        "--version",
        action="version",
        version="FlexiStore 0.2.0"
    )

    return parser


def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = create_parser()
    return parser.parse_args(args)
