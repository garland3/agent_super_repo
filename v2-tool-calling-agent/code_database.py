from typing import Dict, Any
import sqlite3
from datetime import datetime
import os
from pathlib import Path

# Tool Specification
TOOL_SPEC = {
    "name": "code_database",
    "description": "Manages a SQLite database of code snippets with function signatures and descriptions",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "The action to perform on the database",
                "enum": ["add", "get", "search"]
            },
            "function_signature": {
                "type": "string",
                "description": "The function signature or method declaration"
            },
            "short_description": {
                "type": "string",
                "description": "Brief description of what the code does"
            },
            "code": {
                "type": "string",
                "description": "The actual code snippet"
            },
            "snippet_id": {
                "type": "integer",
                "description": "ID of the code snippet to retrieve"
            },
            "query": {
                "type": "string",
                "description": "Search term to find in descriptions or code"
            },
            "rating_0_to_5": {
                "type": "integer",
                "description": "Rating of the code snippet from 0 to 5"
            },
            "reason_for_rating": {
                "type": "string",
                "description": "Explanation for the given rating"
            }
        },
        "required": ["action"]
    }
}

class CodeDatabase:
    def __init__(self):
        db_path = Path(__file__).parent / "code_snippets.db"
        self.conn = sqlite3.connect(str(db_path))
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        # Drop the old table to recreate with new schema
        cursor.execute('DROP TABLE IF EXISTS code_snippets')
        
        # Create the table with new schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_signature TEXT NOT NULL,
                short_description TEXT NOT NULL,
                code TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                rating_0_to_5 INTEGER DEFAULT NULL,
                reason_for_rating TEXT DEFAULT NULL
            )
        ''')
        self.conn.commit()

    def add_code(self, function_signature: str, short_description: str, code: str, rating_0_to_5: int = None, reason_for_rating: str = None) -> int:
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute(
            '''INSERT INTO code_snippets 
               (function_signature, short_description, code, timestamp, rating_0_to_5, reason_for_rating) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (function_signature, short_description, code, timestamp, rating_0_to_5, reason_for_rating)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_code(self, snippet_id: int) -> dict:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM code_snippets WHERE id = ?', (snippet_id,))
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'function_signature': result[1],
                'short_description': result[2],
                'code': result[3],
                'timestamp': result[4],
                'rating_0_to_5': result[5],
                'reason_for_rating': result[6]
            }
        return None

    def search_code(self, query: str) -> list:
        cursor = self.conn.cursor()
        search_pattern = f'%{query}%'
        cursor.execute('''
            SELECT * FROM code_snippets 
            WHERE function_signature LIKE ? 
            OR short_description LIKE ? 
            OR code LIKE ?
        ''', (search_pattern, search_pattern, search_pattern))
        results = cursor.fetchall()
        return [
            {
                'id': r[0],
                'function_signature': r[1],
                'short_description': r[2],
                'code': r[3],
                'timestamp': r[4],
                'rating_0_to_5': r[5],
                'reason_for_rating': r[6]
            }
            for r in results
        ]

    def __del__(self):
        self.conn.close()

# Singleton instance
db = CodeDatabase()

def code_database(action: str, **kwargs) -> Dict[str, Any]:
    """
    Manage code snippets in a SQLite database
    
    Args:
        action (str): The action to perform - 'add', 'get', or 'search'
        **kwargs: Additional arguments based on the action:
            For 'add':
                function_signature (str): The function signature
                short_description (str): Brief description
                code (str): The code snippet
                rating_0_to_5 (int, optional): Rating from 0 to 5
                reason_for_rating (str, optional): Explanation for rating
            For 'get':
                snippet_id (int): ID of snippet to retrieve
            For 'search':
                query (str): Search term
    
    Returns:
        Dict: Result dictionary containing either:
            - Success case: Relevant output data
            - Error case: {"error": "error message"}
    """
    try:
        if action == "add":
            required = ["function_signature", "short_description", "code"]
            if not all(k in kwargs for k in required):
                return {"error": "Missing required parameters for add action"}
            
            # Validate rating if provided
            if "rating_0_to_5" in kwargs:
                rating = kwargs["rating_0_to_5"]
                if not isinstance(rating, int) or rating < 0 or rating > 5:
                    return {"error": "rating_0_to_5 must be an integer between 0 and 5"}
            
            snippet_id = db.add_code(
                kwargs["function_signature"],
                kwargs["short_description"],
                kwargs["code"],
                kwargs.get("rating_0_to_5"),
                kwargs.get("reason_for_rating")
            )
            return {
                "result": {
                    "id": snippet_id,
                    "message": "Code snippet added successfully"
                }
            }

        elif action == "get":
            if "snippet_id" not in kwargs:
                return {"error": "Missing snippet_id parameter"}
            
            result = db.get_code(kwargs["snippet_id"])
            if result:
                return {"result": result}
            return {"error": "Code snippet not found"}

        elif action == "search":
            if "query" not in kwargs:
                return {"error": "Missing query parameter"}
            
            results = db.search_code(kwargs["query"])
            return {
                "result": {
                    "results": results,
                    "count": len(results)
                }
            }

        else:
            return {"error": f"Invalid action: {action}"}

    except Exception as e:
        return {"error": str(e)}
