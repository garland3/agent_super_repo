from colorama import init, Fore, Style
import logging
from claude_processor import ClaudeProcessor, IOHandler
from utils import load_prompt_template, load_tool_specs

# Initialize colorama
init()

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def cli_input() -> str:
    return input(f"\n{Fore.YELLOW}What would you like to do? (or 'exit' to quit): {Style.RESET_ALL}")

def cli_output(message: str):
    print(f"\n{Fore.GREEN}Response: {message}{Style.RESET_ALL}")

def cli_log(message: str):
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
    
    while True:
        try:
            # Get user input
            user_input = io_handler.get_input()
            if user_input.lower() == 'exit':
                break
            
            # Handle clear command
            if user_input.lower() == 'clear':
                processor.clear_history()
                print(f"{Fore.WHITE}Message history cleared!{Style.RESET_ALL}")
                continue
            
            # Process input and get response
            response = processor.process_user_input(user_input, tools, prompt_template)
            
            # Output response
            io_handler.send_output(response)
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Error occurred: {e}", exc_info=True)
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    print(f"\n{Fore.WHITE}Goodbye!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
