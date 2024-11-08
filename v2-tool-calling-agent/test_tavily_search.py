import pytest
from tools.tavily_search import tavily_search
import yaml
from unittest.mock import patch, mock_open, MagicMock

# Sample mock response data
MOCK_SEARCH_RESPONSE = {
    "results": [
        {
            "title": "Test Result",
            "url": "https://test.com",
            "content": "Test content"
        }
    ],
    "query": "test query"
}

# Mock secrets.yaml content
MOCK_SECRETS = """
default:
    tavily_api_key: "test_key"
"""

def test_tavily_search_basic():
    """Test basic search with mocked API response"""
    with patch("builtins.open", mock_open(read_data=MOCK_SECRETS)):
        with patch('tools.tavily_search.TavilyClient') as mock_client:
            # Setup mock
            mock_instance = mock_client.return_value
            mock_instance.search.return_value = MOCK_SEARCH_RESPONSE
            
            # Test basic search
            result = tavily_search("test query", "basic")
            
            # Verify the result
            assert "result" in result
            assert result["result"] == MOCK_SEARCH_RESPONSE
            
            # Verify correct parameters were used
            mock_instance.search.assert_called_once_with(
                query="test query",
                search_depth="basic"
            )

def test_tavily_search_deep():
    """Test deep search with mocked API response"""
    with patch("builtins.open", mock_open(read_data=MOCK_SECRETS)):
        with patch('tools.tavily_search.TavilyClient') as mock_client:
            # Setup mock
            mock_instance = mock_client.return_value
            mock_instance.search.return_value = MOCK_SEARCH_RESPONSE
            
            # Test deep search
            result = tavily_search("test query", "deep")
            
            # Verify the result
            assert "result" in result
            assert result["result"] == MOCK_SEARCH_RESPONSE
            
            # Verify correct parameters were used
            mock_instance.search.assert_called_once_with(
                query="test query",
                search_depth="deep"
            )

def test_tavily_search_missing_api_key():
    """Test behavior when API key is missing"""
    mock_secrets = """
    default:
        other_key: "value"
    """
    with patch("builtins.open", mock_open(read_data=mock_secrets)):
        result = tavily_search("test query")
        assert "error" in result
        assert "API key not found" in result["error"]

def test_tavily_search_api_error():
    """Test handling of API errors"""
    with patch("builtins.open", mock_open(read_data=MOCK_SECRETS)):
        with patch('tools.tavily_search.TavilyClient') as mock_client:
            # Setup mock to raise an exception
            mock_instance = mock_client.return_value
            mock_instance.search.side_effect = Exception("API Error")
            
            # Test error handling
            result = tavily_search("test query")
            
            # Verify error handling
            assert "error" in result
            assert "Tavily search failed" in result["error"]
            assert "API Error" in result["error"]

def test_tavily_search_default_depth():
    """Test search with default depth parameter"""
    with patch("builtins.open", mock_open(read_data=MOCK_SECRETS)):
        with patch('tools.tavily_search.TavilyClient') as mock_client:
            # Setup mock
            mock_instance = mock_client.return_value
            mock_instance.search.return_value = MOCK_SEARCH_RESPONSE
            
            # Test without specifying depth
            result = tavily_search("test query")
            
            # Verify the result and default depth
            assert "result" in result
            mock_instance.search.assert_called_once_with(
                query="test query",
                search_depth="basic"
            )

def test_tavily_search_yaml_file_error():
    """Test handling of YAML file read error"""
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = Exception("File read error")
        result = tavily_search("test query")
        assert "error" in result
        assert "API key not found" in result["error"]
