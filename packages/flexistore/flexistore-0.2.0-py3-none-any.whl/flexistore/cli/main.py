"""Main CLI entry point for FlexiStore."""

import sys
from typing import Optional

try:
    from .args import parse_args
    from .config import create_storage_manager, get_default_provider
    from .interface import run_interactive_cli
    from .utils import print_error, print_info
except ImportError as e:
    print(f"Error importing CLI modules: {e}")
    print("Please ensure FlexiStore is properly installed: pip install -e .")
    sys.exit(1)


def main(args: Optional[list] = None) -> None:
    """Main CLI entry point."""
    try:
        # Parse command line arguments
        parsed_args = parse_args(args)
        
        # Determine provider
        provider = parsed_args.provider or get_default_provider()
        
        print_info(f"Starting FlexiStore CLI with {provider.upper()} provider...")
        
        # Create storage manager
        try:
            manager = create_storage_manager(provider, parsed_args.verify_ssl)
        except Exception as e:
            print_error(f"Failed to create storage manager: {e}")
            print_info("Please check your configuration and credentials.")
            sys.exit(1)
        
        # Run interactive CLI
        run_interactive_cli(manager, provider)
        
    except KeyboardInterrupt:
        print_info("\n\nFlexiStore CLI interrupted by user. Goodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()