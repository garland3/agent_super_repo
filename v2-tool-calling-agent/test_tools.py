import unittest
from tools.tavily_search import tavily_search
import os

class TestTavilySearch(unittest.TestCase):
    def setUp(self):
        # Ensure API key is available for testing
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            self.skipTest("Tavily API key not found in environment variables")

    def test_basic_search(self):
        """Test basic search functionality"""
        result = tavily_search("Who is Leo Messi?")
        self.assertIn("result", result)
        self.assertNotIn("error", result)

    def test_deep_search(self):
        """Test deep search functionality"""
        result = tavily_search("Who is Leo Messi?", search_depth="deep")
        self.assertIn("result", result)
        self.assertNotIn("error", result)

    def test_invalid_search_depth(self):
        """Test error handling for invalid search depth"""
        with self.assertRaises(Exception):
            tavily_search("test query", search_depth="invalid_depth")

    def test_empty_query(self):
        """Test error handling for empty query"""
        result = tavily_search("")
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main()
