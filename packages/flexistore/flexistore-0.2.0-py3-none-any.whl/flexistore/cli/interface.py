"""CLI user interface and menu system for FlexiStore."""

from typing import Dict, Callable, Optional

from flexistore.core.base import StorageManager
from .commands import FileOperations
from .utils import print_error, print_info


class CLIMenu:
    """Interactive CLI menu system."""
    
    def __init__(self, manager: StorageManager, provider: str):
        self.manager = manager
        self.provider = provider
        self.file_ops = FileOperations(manager)
        self.running = True
        
        # Menu options mapping
        self.menu_options: Dict[str, Dict[str, any]] = {
            "1": {
                "title": "Upload a file",
                "icon": "📤",
                "handler": self.file_ops.upload_file
            },
            "2": {
                "title": "List files",
                "icon": "📋", 
                "handler": self.file_ops.list_files
            },
            "3": {
                "title": "Download a file",
                "icon": "📥",
                "handler": self.file_ops.download_file
            },
            "4": {
                "title": "Delete a file",
                "icon": "🗑️",
                "handler": self.file_ops.delete_file
            },
            "5": {
                "title": "Download folder",
                "icon": "📁",
                "handler": self.file_ops.download_folder
            },
            "0": {
                "title": "Exit",
                "icon": "🚪",
                "handler": self._exit
            }
        }
    
    def print_header(self) -> None:
        """Print the CLI header with provider info."""
        print(f"\n{'=' * 50}")
        print(f"🗄️  FlexiStore CLI - {self.provider.upper()} Storage")
        print(f"{'=' * 50}")
    
    def print_menu(self) -> None:
        """Print the main menu options."""
        print("\n📋 Available Operations:")
        print("-" * 30)
        
        for key, option in self.menu_options.items():
            print(f"  {key}) {option['icon']} {option['title']}")
        
        print("-" * 30)
    
    def get_user_choice(self) -> str:
        """Get and validate user menu choice."""
        while True:
            choice = input("Select an option: ").strip()
            if choice in self.menu_options:
                return choice
            print_error(f"Invalid choice '{choice}'. Please try again.")
    
    def execute_choice(self, choice: str) -> bool:
        """Execute the selected menu option."""
        option = self.menu_options[choice]
        handler = option["handler"]
        
        try:
            return handler()
        except KeyboardInterrupt:
            print_info("\nOperation cancelled by user.")
            return False
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            return False
    
    def _exit(self) -> bool:
        """Handle exit command."""
        print_info("Goodbye! 👋")
        self.running = False
        return True
    
    def run(self) -> None:
        """Run the interactive CLI menu."""
        try:
            # Initialize the storage manager
            print_info(f"Initializing {self.provider.upper()} storage connection...")
            self.manager.initialize()
            
            self.print_header()
            
            while self.running:
                self.print_menu()
                choice = self.get_user_choice()
                
                if choice == "0":
                    self._exit()
                    break
                
                success = self.execute_choice(choice)
                
                if not success:
                    print_info("Operation completed with errors.")
                
                # Add spacing between operations
                if self.running:
                    input("\nPress Enter to continue...")
        
        except KeyboardInterrupt:
            print_info("\n\nExiting FlexiStore CLI. Goodbye! 👋")
        except Exception as e:
            print_error(f"Fatal error: {e}")
            print_info("Exiting FlexiStore CLI.")
        finally:
            # Clean up resources
            try:
                if hasattr(self.manager, 'close'):
                    self.manager.close()
            except Exception:
                pass  # Ignore cleanup errors


def run_interactive_cli(manager: StorageManager, provider: str) -> None:
    """Run the interactive CLI with the given storage manager."""
    menu = CLIMenu(manager, provider)
    menu.run()
