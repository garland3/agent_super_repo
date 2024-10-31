import anthropic
import json
import logging
import time
from typing import Dict, List, Tuple, Callable, Any
from dynaconf import Dynaconf

# Load configuration
settings = Dynaconf(
    settings_files=['config/settings.yaml', 'config/secrets.yaml'],
    environments=True
)

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
        
    def process_tool_iteration(self, tools: List[Dict], prompt_template: str) -> Tuple[bool, str]:
        """Handle a single tool use iteration"""
        self.io_handler.log("🤖 Generating response from Claude...")
        start_time = time.time()
        
        response = self.client.messages.create(
            model=settings.model,
            max_tokens=settings.max_tokens,
            tools=tools,
            messages=self.message_history
        )
        
        elapsed_time = time.time() - start_time
        self.io_handler.log(f"⏱️ Response generated in {elapsed_time:.2f} seconds")
        
        tool_use_blocks = [block for block in response.content if block.type == 'tool_use']
        
        if not tool_use_blocks:
            # If no tool use requested, return the response
            assistant_response = response.content[0].text
            self.message_history.append({"role": "assistant", "content": assistant_response})
            self.io_handler.log("✨ Direct response (no tool use)")
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
            self.io_handler.log(f"\n🔧 Tool Called: {tool_use['name']}")
            self.io_handler.log("📥 Input Parameters:")
            for key, value in tool_use['input'].items():
                self.io_handler.log(f"   • {key}: {value}")
            
            # Execute the tool
            start_time = time.time()
            result = handle_tool_call(tool_use)
            elapsed_time = time.time() - start_time
            
            # Log tool result
            self.io_handler.log(f"⏱️ Tool execution completed in {elapsed_time:.2f} seconds")
            self.io_handler.log("📤 Tool Result:")
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
            final_response = json.dumps(result)
            
        return False, final_response

    def process_user_input(self, user_input: str, tools: List[Dict], prompt_template: str, max_iterations: int = 5) -> str:
        """Process user input and return final response"""
        self.io_handler.log("\n📝 Processing new user input...")
        self.message_history.append({"role": "user", "content": user_input})
        
        iteration_count = 0
        final_response = ""
        
        while iteration_count < max_iterations:
            iteration_count += 1
            self.io_handler.log(f"\n🔄 Starting iteration {iteration_count}/{max_iterations}")
            
            should_stop, response = self.process_tool_iteration(tools, prompt_template)
            final_response = response
            
            if should_stop:
                self.io_handler.log("✅ Processing completed")
                break
                
            if iteration_count == max_iterations:
                final_response = f"Reached maximum number of tool iterations ({max_iterations})"
                self.io_handler.log("⚠️ Maximum iterations reached")
                
        return final_response

    def clear_history(self):
        """Clear message history"""
        self.message_history = []
        self.io_handler.log("🧹 Message history cleared")
