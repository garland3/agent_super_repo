from typing import Dict, Any
from tavily import TavilyClient
import yaml

# Tool Specification
TOOL_SPEC = {
    "name": "tavily_search",
    "description": "Perform a web search using the Tavily API to get high-quality, relevant search results",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to execute"
            },
            "search_depth": {
                "type": "string",
                "description": "The depth of search to perform - basic for faster results, deep for more comprehensive search",
                "enum": ["basic", "deep"],
                "default": "basic"
            }
        },
        "required": ["query"]
    }
}

def _get_api_key() -> str:
    """Get Tavily API key from secrets.yaml"""
    try:
        with open("config/secrets.yaml", 'r') as f:
            secrets = yaml.safe_load(f)
            return secrets.get('default', {}).get('tavily_api_key')
    except Exception as e:
        return None

def tavily_search(query: str, search_depth: str = "basic") -> Dict:
    """
    Perform a web search using the Tavily API.
    
    Args:
        query (str): The search query to execute
        search_depth (str): The depth of search - 'basic' or 'deep'
        
    Returns:
        Dict: Result dictionary containing either:
            - Success case: Search results from Tavily
            - Error case: {"error": "error message"}
    """
    try:
        api_key = _get_api_key()
        if not api_key:
            return {"error": "Tavily API key not found in secrets.yaml"}

        client = TavilyClient(api_key=api_key)
        
        # Execute search with specified parameters
        response = client.search(
            query=query,
            search_depth=search_depth
        )
        
        return {"result": response}
        
    except Exception as e:
        return {"error": f"Tavily search failed: {str(e)}"}
