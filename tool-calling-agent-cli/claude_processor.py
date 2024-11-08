"""
Core module for processing user inputs through Claude AI and managing tool executions.
This module handles the interaction with Anthropic's Claude API, manages message history,
and coordinates tool usage in a controlled iteration cycle.
"""

import anthropic
import json
import logging
import time
import datetime
from typing import Dict, List, Tuple, Callable, Any, Optional
from dynaconf import Dynaconf

# Load configuration from YAML files
# settings.yaml contains general settings
# secrets.yaml contains sensitive data like API keys
settings = Dynaconf(
    settings_files=['config/settings.yaml', 'config/secrets.yaml'],
    environments=True
)

class IOHandler:
    """
    Handles input/output operations for the Claude processor.
    Provides a flexible interface for different I/O implementations (CLI, GUI, etc.)
    
    Attributes:
        get_input: Function to get user input
        send_output: Function to display output to user
        log: Function to log system messages and debug info
    """
    def __init__(self, input_func: Callable[[], str], output_func: Callable[[str], None], log_func: Callable[[str], None] = print):
        self.get_input = input_func
        self.send_output = output_func
        self.log = log_func

class ClaudeProcessor:
    """
    Main processor class that handles interactions with Claude AI.
    Manages message history, processes tool usage, and coordinates the 
    conversation flow between user input and Claude's responses.
    
    Attributes:
        client: Anthropic API client instance
        io_handler: IOHandler instance for managing I/O operations
        message_history: List of previous messages in the conversation
    """
    def __init__(self, io_handler: IOHandler):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.io_handler = io_handler
        self.message_history = []
        
    def process_tool_iteration(self, tools: List[Dict], prompt_template: str, 
                             tool_choice: Optional[Dict] = None,
                             disable_parallel_tool_use: bool = False) -> Tuple[bool, str]:
        """
        Handles a single iteration of tool processing with Claude.
        
        This method:
        1. Generates a response from Claude
        2. Checks if tool use is requested
        3. If no tool use, returns the direct response
        4. If tool use requested, executes the tool and formats result
        
        Args:
            tools: List of available tools and their specifications
            prompt_template: Template for formatting tool results
            tool_choice: Optional dict specifying tool choice behavior:
                - {"type": "auto"} (default) - Claude decides whether to use tools
                - {"type": "any"} - Forces Claude to use one of the provided tools
                - {"type": "tool", "name": "tool_name"} - Forces use of specific tool
            disable_parallel_tool_use: If True, ensures Claude uses at most one tool
                
        Returns:
            Tuple[bool, str]:
                - Boolean indicating if processing should stop
                - Response string (either direct response or tool result)
        """
        self.io_handler.log("🤖 Generating response from Claude...")
        start_time = time.time()
        
        # Add current date/time to system prompt
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        system_prompt = f"Current date and time: {current_datetime}\n\nYou are Cline, a highly skilled software engineer with extensive knowledge in many programming languages, frameworks, design patterns, and best practices."
        
        # Prepare API request parameters
        api_params = {
            "model": settings.model,
            "max_tokens": settings.max_tokens,
            "tools": tools,
            "messages": self.message_history,
            "system": system_prompt
        }
        
        # Add tool choice configuration if specified
        if tool_choice:
            api_params["tool_choice"] = tool_choice
            
        # Configure parallel tool use
        if disable_parallel_tool_use:
            if not tool_choice:
                api_params["tool_choice"] = {"type": "auto"}
            api_params["tool_choice"]["disable_parallel_tool_use"] = True
        
        # Get response from Claude API
        response = self.client.messages.create(**api_params)
        
        elapsed_time = time.time() - start_time
        self.io_handler.log(f"⏱️ Response generated in {elapsed_time:.2f} seconds")
        
        # Extract tool use blocks from response
        tool_use_blocks = [block for block in response.content if block.type == 'tool_use']
        
        # Handle direct response (no tool use)
        if not tool_use_blocks:
            assistant_response = response.content[0].text
            self.message_history.append({"role": "assistant", "content": assistant_response})
            self.io_handler.log("✨ Direct response (no tool use)")
            return True, assistant_response
        
        # Add assistant's response with tool use to message history
        self.message_history.append({"role": "assistant", "content": response.content})
        
        # Process each tool use request
        final_response = ""
        for tool_block in tool_use_blocks:
            from utils import handle_tool_call  # Import here to avoid circular imports
            
            tool_use = {
                "name": tool_block.name,
                "input": tool_block.input
            }
            
            # Log detailed tool invocation information
            self.io_handler.log(f"\n🔧 Tool Called: {tool_use['name']}")
            self.io_handler.log("📥 Input Parameters:")
            for key, value in tool_use['input'].items():
                self.io_handler.log(f"   • {key}: {value}")
            
            # Execute tool and measure performance
            start_time = time.time()
            try:
                result = handle_tool_call(tool_use)
                is_error = False
            except Exception as e:
                result = str(e)
                is_error = True
            elapsed_time = time.time() - start_time
            
            # Log detailed tool execution results
            self.io_handler.log(f"⏱️ Tool execution completed in {elapsed_time:.2f} seconds")
            self.io_handler.log("📤 Tool Result:")
            if isinstance(result, dict):
                for key, value in result.items():
                    self.io_handler.log(f"   • {key}: {value}")
            else:
                self.io_handler.log(f"   {result}")
            
            # Format tool result as specified in Claude docs
            tool_result = {
                "type": "tool_result",
                "tool_use_id": tool_block.id,
                "content": [{"type": "text", "text": json.dumps(result)}]
            }
            if is_error:
                tool_result["is_error"] = True
            
            # Update conversation history with tool result
            self.message_history.append({
                "role": "user", 
                "content": [tool_result]
            })
            final_response = json.dumps(result)
            
        return False, final_response

    def process_user_input(self, user_input: str, tools: List[Dict], prompt_template: str,
                          tool_choice: Optional[Dict] = None,
                          disable_parallel_tool_use: bool = False) -> str:
        """
        Main entry point for processing user input through Claude.
        Manages the overall conversation flow and tool iteration cycle.
        
        This method:
        1. Adds user input to message history
        2. Iteratively processes tool usage up to settings.max_iterations
        3. Handles completion conditions and iteration limits
        4. Breaks early if a direct response is received
        
        Args:
            user_input: The user's input text
            tools: List of available tools
            prompt_template: Template for formatting tool results
            tool_choice: Optional dict specifying tool choice behavior
            disable_parallel_tool_use: If True, ensures Claude uses at most one tool
            
        Returns:
            str: Final response after processing
        """
        self.io_handler.log("\n📝 Processing new user input...")
        self.message_history.append({"role": "user", "content": user_input})
        
        iteration_count = 0
        final_response = ""
        
        # Main processing loop
        while iteration_count < settings.max_iterations:
            iteration_count += 1
            self.io_handler.log(f"\n🔄 Starting iteration {iteration_count}/{settings.max_iterations}")
            
            should_stop, response = self.process_tool_iteration(
                tools, 
                prompt_template,
                tool_choice=tool_choice,
                disable_parallel_tool_use=disable_parallel_tool_use
            )
            final_response = response
            
            # Break if we got a direct response
            if should_stop:
                self.io_handler.log("✅ Processing completed - direct response received")
                break
                
            if iteration_count == settings.max_iterations:
                final_response = f"Reached maximum number of tool iterations ({settings.max_iterations})"
                self.io_handler.log("⚠️ Maximum iterations reached")
                
        return final_response

    def clear_history(self):
        """
        Resets the conversation by clearing message history.
        Useful for starting fresh conversations or managing memory usage.
        """
        self.message_history = []
        self.io_handler.log("🧹 Message history cleared")
