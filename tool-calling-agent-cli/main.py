"""
Main CLI application that provides an interactive interface for processing user inputs through Claude.
The application handles tool execution, input/output formatting, and message history management.
"""

from colorama import init, Fore, Style
import logging
from claude_processor import ClaudeProcessor, IOHandler
from utils import load_prompt_template, load_tool_specs

# Initialize colorama for cross-platform colored terminal output
init()

# Configure logging with timestamp, level, and message format
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def cli_input() -> str:
    """
    Prompts the user for input with yellow-colored text.
    Returns the user's input as a string.
    The user can type 'exit' to quit or 'clear' to reset message history.
    """
    return input(f"\n{Fore.YELLOW}What would you like to do? (or 'exit' to quit): {Style.RESET_ALL}")

def cli_output(message: str):
    """
    Displays Claude's response in green-colored text.
    Args:
        message: The response text to display
    """
    print(f"\n{Fore.GREEN}Response: {message}{Style.RESET_ALL}")

def cli_log(message: str):
    """
    Formats and displays different types of log messages with distinct colors:
    - Tool invocations in magenta
    - Tool arguments in blue 
    - Tool results in cyan
    - Other messages in default color
    
    Args:
        message: The log message to display
    """
    if message.startswith("\nTool Invoked:"):
        print(f"{Fore.MAGENTA}{message}{Style.RESET_ALL}")
    elif message.startswith("Arguments:"):
        print(f"{Fore.BLUE}{message}{Style.RESET_ALL}")
    elif message.startswith("Tool Result:"):
        print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")
    else:
        print(message)

def main():
    """
    Main application loop that:
    1. Sets up IO handling for the CLI interface
    2. Initializes the Claude processor for handling user inputs
    3. Loads available tools and prompt template
    4. Displays available tools to the user
    5. Enters main interaction loop:
        - Gets user input
        - Handles special commands (exit/clear)
        - Processes input through Claude
        - Displays responses
        - Handles errors gracefully
    """
    # Initialize IO handler with CLI-specific input/output functions
    io_handler = IOHandler(cli_input, cli_output, cli_log)
    
    # Create Claude processor instance for handling user inputs
    processor = ClaudeProcessor(io_handler)
    
    # Load available tools and prompt template from configuration
    tools = load_tool_specs()
    prompt_template = load_prompt_template()
    
    # Display available tools to user at startup
    print(f"{Fore.WHITE}Available tools:{Style.RESET_ALL}")
    for tool in tools:
        print(f"{Fore.WHITE}- {tool['name']}: {tool['description']}{Style.RESET_ALL}")
    
    # Main interaction loop
    while True:
        try:
            # Get user input and handle exit command
            user_input = io_handler.get_input()
            if user_input.lower() == 'exit':
                break
            
            # Handle clear command to reset message history
            if user_input.lower() == 'clear':
                processor.clear_history()
                print(f"{Fore.WHITE}Message history cleared!{Style.RESET_ALL}")
                continue
            
            # Process input through Claude and get response
            response = processor.process_user_input(user_input, tools, prompt_template)
            
            # Display Claude's response
            io_handler.send_output(response)
                
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            break
        except Exception as e:
            # Log full error details and display user-friendly error message
            logging.error(f"Error occurred: {e}", exc_info=True)
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}Goodbye!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
