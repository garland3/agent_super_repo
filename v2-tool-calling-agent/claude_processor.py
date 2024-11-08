import anthropic
import json
import logging
import time
from typing import Dict, List, Tuple, Callable, Any
from dynaconf import Dynaconf
from utils import load_system_prompt

# Load configuration
settings = Dynaconf(
    settings_files=['config/settings.yaml', 'config/secrets.yaml'],
    environments=True
)

def sanitize_log_message(message):
    """Remove emojis and other problematic Unicode characters from log messages"""
    return ''.join(char for char in message if ord(char) < 65536)

class IOHandler:
    def __init__(self, input_func: Callable[[], str], output_func: Callable[[str], None], log_func: Callable[[str], None] = print):
        self.get_input = input_func
        self.send_output = output_func
        self.log = log_func

class ClaudeProcessor:
    def __init__(self, io_handler: IOHandler):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.io_handler = io_handler
        self.message_history = []
        self.first_message = True
        
    def process_tool_iteration(self, tools: List[Dict], prompt_template: str) -> Tuple[bool, str]:
        """Handle a single tool use iteration"""
        self.io_handler.log("Generating response from Claude...")
        start_time = time.time()
        
        logging.info(f"Message history for this iteration: {json.dumps(self.message_history, indent=2)}")
        
        response = self.client.messages.create(
            model=settings.model,
            max_tokens=settings.max_tokens,
            tools=tools,
            messages=self.message_history
        )
        
        elapsed_time = time.time() - start_time
        self.io_handler.log(f"Response generated in {elapsed_time:.2f} seconds")
        logging.info(f"Claude response generated in {elapsed_time:.2f} seconds")
        
        # Log the text content instead of trying to JSON serialize the entire response
        content_texts = [block.text if hasattr(block, 'text') else str(block) for block in response.content]
        logging.info(f"Response content texts: {json.dumps(content_texts, indent=2)}")
        
        tool_use_blocks = [block for block in response.content if block.type == 'tool_use']
        
        if not tool_use_blocks:
            # If no tool use requested, return the response
            assistant_response = response.content[0].text
            self.message_history.append({"role": "assistant", "content": assistant_response})
            self.io_handler.log("Direct response (no tool use)")
            logging.info(f"Assistant direct response: {assistant_response}")
            return True, assistant_response
        
        # Process tool use
        final_response = ""
        for tool_block in tool_use_blocks:
            from utils import handle_tool_call  # Import here to avoid circular imports
            
            tool_use = {
                "name": tool_block.name,
                "input": tool_block.input
            }
            
            # Log tool invocation with detailed formatting
            self.io_handler.log(f"\nTool Called: {tool_use['name']}")
            self.io_handler.log("Input Parameters:")
            logging.info(f"Tool called: {tool_use['name']}")
            logging.info(f"Tool input parameters: {json.dumps(tool_use['input'], indent=2)}")
            
            for key, value in tool_use['input'].items():
                self.io_handler.log(f"   • {key}: {value}")
            
            # Execute the tool
            start_time = time.time()
            result = handle_tool_call(tool_use)
            elapsed_time = time.time() - start_time
            
            # Log tool result
            self.io_handler.log(f"Tool execution completed in {elapsed_time:.2f} seconds")
            self.io_handler.log("Tool Result:")
            logging.info(f"Tool execution completed in {elapsed_time:.2f} seconds")
            logging.info(f"Tool result: {json.dumps(result, indent=2)}")
            
            if isinstance(result, dict):
                for key, value in result.items():
                    self.io_handler.log(f"   • {key}: {value}")
            else:
                self.io_handler.log(f"   {result}")
            
            # Format the prompt with the tool result
            formatted_prompt = prompt_template.format(
                user_query="Continue processing with tool result",
                tool_name=tool_block.name,
                tool_params=json.dumps(tool_block.input),
                tool_response=json.dumps(result)
            )
            
            # Add the tool result to history
            self.message_history.append({"role": "user", "content": formatted_prompt})
            logging.info(f"Added tool result to message history: {formatted_prompt}")
            final_response = json.dumps(result)
            
        return False, final_response

    def process_user_input(self, user_input: str, tools: List[Dict], prompt_template: str, max_iterations: int = 25) -> str:
        """Process user input and return final response"""
        self.io_handler.log("\nProcessing new user input...")
        logging.info(f"Processing new user input: {user_input}")
        
        # Track starting message index
        start_message_index = len(self.message_history)
        
        # For the first message, prepend the system prompt
        if self.first_message:
            system_prompt = load_system_prompt()
            user_input = f"{system_prompt}\n\n{user_input}"
            self.first_message = False
            logging.info("Added system prompt to first message")
            
        self.message_history.append({"role": "user", "content": user_input})
        logging.info("Added user input to message history")
        
        iteration_count = 0
        final_response = ""
        
        while iteration_count < max_iterations:
            iteration_count += 1
            self.io_handler.log(f"\nStarting iteration {iteration_count}/{max_iterations}")
            logging.info(f"Starting iteration {iteration_count}/{max_iterations}")
            
            # Check if we should ask user to continue every 5 iterations
            if iteration_count > 1 and iteration_count % 5 == 0:
                continue_response = self.io_handler.get_input(f"\nCompleted {iteration_count} iterations. Continue processing? (y/n): ")
                logging.info(f"User prompted to continue after {iteration_count} iterations. Response: {continue_response}")
                if continue_response.lower() != 'y':
                    final_response = f"Processing stopped at user request after {iteration_count} iterations"
                    self.io_handler.log("Processing stopped by user")
                    logging.info("Processing stopped by user request")
                    break
            
            should_stop, response = self.process_tool_iteration(tools, prompt_template)
            final_response = response
            
            if should_stop:
                self.io_handler.log("Processing completed")
                logging.info("Processing completed successfully")
                break
                
            if iteration_count == max_iterations:
                final_response = f"Reached maximum number of tool iterations ({max_iterations})"
                self.io_handler.log("Maximum iterations reached")
                logging.info(f"Maximum iterations ({max_iterations}) reached")
        
        # Log completion
        end_message_index = len(self.message_history) - 1
        messages_processed = end_message_index - start_message_index + 1
        logging.info(f"Total messages processed in this interaction: {messages_processed}")
                
        return final_response

    def clear_history(self):
        """Clear message history"""
        self.message_history = []
        self.first_message = True
        self.io_handler.log("Message history cleared")
        logging.info("Message history cleared")
