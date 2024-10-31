import anthropic
from typing import Dict, List
import json
from dynaconf import Dynaconf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import utility functions
from utils import load_prompt_template, load_tool_specs, handle_tool_call

# Load configuration
settings = Dynaconf(
    settings_files=['config/settings.yaml', 'config/secrets.yaml'],
    environments=True
)

def main():
    # Initialize Anthropic client with API key from settings
    client = anthropic.Anthropic(
        api_key=settings.anthropic_api_key
    )
    
    # Load tool specifications and prompt template
    tools = load_tool_specs()
    prompt_template = load_prompt_template()
    
    print("Available tools:")
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")
    
    while True:
        try:
            # Get user input
            user_input = input("\nWhat would you like to do? (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
                
            # Log tools before creating message
            logging.info(f"Creating message with tools: {json.dumps(tools, indent=2)}")
            
            # Create message with Claude
            response = client.messages.create(
                model=settings.model,
                max_tokens=settings.max_tokens,
                tools=tools,
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            
            # Log the response
            logging.info(f"Received response: {response}")
            
            # Check if Claude wants to use a tool
            tool_use_blocks = [block for block in response.content if block.type == 'tool_use']
            
            if tool_use_blocks:
                for tool_block in tool_use_blocks:
                    # Extract tool use details
                    tool_use = {
                        "name": tool_block.name,
                        "input": tool_block.input
                    }
                    
                    # Execute the tool
                    result = handle_tool_call(tool_use)
                    print(f"\nTool Result: {json.dumps(result, indent=2)}")
                    
                    # Format the prompt with the relevant information
                    formatted_prompt = prompt_template.format(
                        user_query=user_input,
                        tool_name=tool_block.name,
                        tool_params=json.dumps(tool_block.input),
                        tool_response=json.dumps(result)
                    )
                    
                    # Send the result back to Claude for final response using the formatted prompt
                    final_response = client.messages.create(
                        model=settings.model,
                        max_tokens=settings.max_tokens,
                        messages=[
                            {"role": "user", "content": formatted_prompt}
                        ]
                    )
                    print(f"\nClaude's Response: {final_response.content[0].text}")
            else:
                # If no tool use, just print Claude's text response
                print(f"\nClaude's Response: {response.content[0].text}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Error occurred: {e}", exc_info=True)
            print(f"Error: {e}")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()
