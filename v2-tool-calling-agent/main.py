from colorama import init, Fore, Style
import logging
from claude_processor import ClaudeProcessor, IOHandler
from utils import load_prompt_template, load_tool_specs
from datetime import datetime
import re
import sys

# Initialize colorama
init()

def sanitize_log_message(message):
    """Remove emojis and other problematic Unicode characters from log messages"""
    return ''.join(char for char in message if ord(char) < 65536)

class UnicodeHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            msg = sanitize_log_message(msg)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# Configure logging to log to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("log.log", mode='a', encoding='utf-8'),  # Added UTF-8 encoding
        UnicodeHandler(sys.stdout)  # Custom handler for console output
    ]
)

# Add session separator
with open("log.log", "a", encoding='utf-8') as f:
    f.write("\n" + "-" * 80 + "\n")
    f.write(f"New Session Started: {datetime.now()}\n")
    f.write("-" * 80 + "\n")

def cli_input() -> str:
    user_input = input(f"\n{Fore.YELLOW}What would you like to do? (or 'exit' to quit): {Style.RESET_ALL}")
    logging.info(f"User Input: {user_input}")
    return user_input

def cli_output(message: str):
    logging.info(f"Assistant Response: {message}")
    print(f"\n{Fore.GREEN}Response: {message}{Style.RESET_ALL}")

def sanitize_input(user_input: str) -> str:
    # Remove any non-printable characters
    sanitized = re.sub(r'[^\x20-\x7E]', '', user_input)
    return sanitized.strip()

def cli_input(message = None) -> str:
    if message:
        print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")
    else:
        user_input = input(f"\n{Fore.YELLOW}What would you like to do? (or 'exit' to quit): {Style.RESET_ALL}")
        sanitized_input = sanitize_input(user_input)
        logging.info(f"User Input: {message}")
        return sanitized_input
    return message

def cli_log(message: str):
    safe_message = sanitize_log_message(message)
    logging.info(safe_message)
    message = sanitize_input(message)
    if message.startswith("\nTool Invoked:"):
        print(f"{Fore.MAGENTA}{message}{Style.RESET_ALL}")
    elif message.startswith("Arguments:"):
        print(f"{Fore.BLUE}{message}{Style.RESET_ALL}")
    elif message.startswith("Tool Result:"):
        print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")
    else:
        print(message)

def main():
    # Initialize IO handler for CLI
    io_handler = IOHandler(cli_input, cli_output, cli_log)
    
    # Initialize Claude processor
    processor = ClaudeProcessor(io_handler)
    
    # Load tool specifications and prompt template
    tools = load_tool_specs()
    prompt_template = load_prompt_template()
    
    print(f"{Fore.WHITE}Available tools:{Style.RESET_ALL}")
    for tool in tools:
        print(f"{Fore.WHITE}- {tool['name']}: {tool['description']}{Style.RESET_ALL}")
        logging.info(f"Available tool: {tool['name']} - {tool['description']}")
    
    while True:
        try:
            # Get user input
            user_input = io_handler.get_input()
            
            # If input is empty after stripping, continue the loop
            if not user_input:
                continue
                
            if user_input.lower() == 'exit':
                logging.info("User requested exit")
                break
            
            # Handle clear command
            if user_input.lower() == 'clear':
                processor.clear_history()
                logging.info("Message history cleared")
                print(f"{Fore.WHITE}Message history cleared!{Style.RESET_ALL}")
                continue
            
            # Process input and get response
            response = processor.process_user_input(user_input, tools, prompt_template)
            
            # Output response
            io_handler.send_output(response)
                
        except KeyboardInterrupt:
            logging.info("Program interrupted by user")
            break
        except Exception as e:
            logging.error(f"Error occurred: {e}", exc_info=True)
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    logging.info("Program terminated")
    print(f"\n{Fore.WHITE}Goodbye!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
