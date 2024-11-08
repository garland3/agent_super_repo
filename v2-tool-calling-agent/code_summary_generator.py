import anthropic
import logging
from dynaconf import Dynaconf

def load_settings():
    """Load settings from settings.yaml"""
    settings = Dynaconf(
        settings_files=['config/settings.yaml', 'config/secrets.yaml'],
        environments=True
    )
    return settings

def get_code_summary(code: str) -> str:
    """Get a concise summary of the code using Claude
    
    Args:
        code (str): The Python code to analyze
        
    Returns:
        str: A concise one-line description of what it does
    """
    logging.info(f"Getting code summary for code:\n{code}")
    
    settings = load_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    
    prompt = f"""Analyze this Python code and provide ONLY a concise one-line description of what it does, including any important arguments or return values. Do not include any other commentary or explanations.

Code to analyze:
```python
{code}
```"""

    logging.info(f"Sending prompt to Claude for code summary:\n{prompt}")

    response = client.messages.create(
        model=settings.model,
        max_tokens=settings.max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    
    summary = response.content[0].text.strip()
    logging.info(f"Received code summary from Claude: {summary}")
    
    return summary

def make_code_generic(code: str) -> str:
    """Make the code more generic and reusable using Claude
    
    Args:
        code (str): The Python code to generalize
        
    Returns:
        str: The generalized version of the code
    """
    logging.info(f"Making code generic for:\n{code}")
    
    settings = load_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    
    prompt = f"""Your function will be reused for building more complex functions. Therefore, you should make it generic and reusable. Rewrite this Python code to:
1. Accept configuration and arguments as parameters instead of hardcoding values
2. Make it more modular and reusable
3. Add proper type hints and docstrings
4. Follow Python best practices
5. Keep the core functionality but make it more flexible
6. Do NOT include a main function. However, show in a comment at the end how to use the core function.

Original code:
```python
{code}
```

Provide ONLY the rewritten code without any explanations or comments beyond docstrings."""

    logging.info(f"Sending prompt to Claude for code generalization:\n{prompt}")

    response = client.messages.create(
        model=settings.model,
        max_tokens=settings.max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    
    generic_code = response.content[0].text.strip()
    logging.info(f"Received generalized code from Claude:\n{generic_code}")
    
    return generic_code
