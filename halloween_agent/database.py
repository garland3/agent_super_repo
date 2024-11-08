import sqlite3
import json
import logging

# Get logger
logger = logging.getLogger(__name__)

def init_db():
    """Initialize SQLite database and create necessary tables"""
    conn = sqlite3.connect('halloween_responses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS llm_responses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  response_data JSON,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_json_response(json_data):
    """
    Save JSON response to SQLite database
    Args:
        json_data: Parsed JSON data to save
    """
    try:
        conn = sqlite3.connect('halloween_responses.db')
        c = conn.cursor()
        c.execute('INSERT INTO llm_responses (response_data) VALUES (?)',
                 [json.dumps(json_data)])
        conn.commit()
        conn.close()
        logger.info("Successfully saved JSON response to database")
    except Exception as e:
        logger.error(f"Error saving to database: {str(e)}")
        raise
