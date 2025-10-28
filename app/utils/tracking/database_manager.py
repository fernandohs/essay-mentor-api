"""
Database manager for token usage tracking.
Handles all SQLite database operations.
"""
import sqlite3
from typing import Optional
from app.models.usage import TokenUsage


class DatabaseManager:
    """Manages SQLite database operations for token tracking."""
    
    def __init__(self, db_path: str = "usage_tracking.db"):
        """Initialize database manager."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create token_usage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS token_usage (
                id TEXT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                function TEXT NOT NULL,
                tokens_input INTEGER NOT NULL,
                tokens_output INTEGER NOT NULL,
                tokens_total INTEGER NOT NULL,
                cost_usd REAL NOT NULL,
                response_time_ms INTEGER NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                fallback_model TEXT,
                retry_count INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_token_usage_timestamp 
            ON token_usage(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_token_usage_function 
            ON token_usage(function)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_token_usage_provider 
            ON token_usage(provider)
        """)
        
        conn.commit()
        conn.close()
    
    def insert_usage(self, usage: TokenUsage) -> bool:
        """
        Insert token usage record into database.
        
        Args:
            usage: TokenUsage record to insert
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO token_usage (
                    id, timestamp, provider, model, function,
                    tokens_input, tokens_output, tokens_total,
                    cost_usd, response_time_ms, status,
                    error_message, fallback_model, retry_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usage.id, usage.timestamp, usage.provider.value, usage.model,
                usage.function.value, usage.tokens_input, usage.tokens_output,
                usage.tokens_total, usage.cost_usd, usage.response_time_ms,
                usage.status.value, usage.error_message, usage.fallback_model,
                usage.retry_count
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of query results
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"Database query error: {e}")
            return []
