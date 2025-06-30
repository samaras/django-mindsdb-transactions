import os
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.db import models
import mindsdb_sdk
from .models import Transaction, Client, Card


class MindsDBUtil:
    """
    Utility class for executing MindsDB SQL queries using mindsdb_sdk
    """
    
    def __init__(self):
        """Initialize the MindsDB connection using mindsdb_sdk"""
        try:
            # Get MindsDB connection parameters from environment or settings
            host = getattr(settings, 'MINDSDB_HOST', 'localhost')
            port = getattr(settings, 'MINDSDB_PORT', 47334)
            username = getattr(settings, 'MINDSDB_USER', None)
            password = getattr(settings, 'MINDSDB_PASSWORD', None)
            
            # Initialize MindsDB connection
            if username and password:
                self.connection = mindsdb_sdk.connect(
                    host=host,
                    port=port,
                    username=username,
                    password=password
                )
            else:
                self.connection = mindsdb_sdk.connect(
                    host=host,
                    port=port
                )
            
            self.server = self.connection.get_server()
            print(f"Successfully connected to MindsDB at {host}:{port}")
            
        except Exception as e:
            print(f"Warning: Could not initialize MindsDB connection: {e}")
            self.connection = None
            self.server = None
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a MindsDB SQL query and return results
        
        Args:
            query: SQL query to execute
            
        Returns:
            List of dictionaries containing query results
        """
        if not self.connection:
            raise Exception("MindsDB connection not available")
        
        try:
            # Execute the query
            result = self.connection.query(query)
            
            # Convert to list of dictionaries
            if hasattr(result, 'fetchall'):
                columns = [desc[0] for desc in result.description]
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:
                # Handle different result formats
                return result.to_dict('records') if hasattr(result, 'to_dict') else []
                
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
    
    def find_wealthy_clients(self, min_age: int = 40, min_income: float = 70000) -> List[Dict[str, Any]]:
        """
        Find clients in wealthy, suburban areas with age and income filtering
        """
        query = f"""
        SELECT
            c.id AS client_id,
            c.address,
            c.current_age,
            c.per_capita_income,
            c.gender
        FROM
            client_kb AS c
        WHERE
            content LIKE 'wealthy, suburban areas' AND 
            c.current_age > {min_age} AND                    
            c.per_capita_income > {min_income};
        """
        return self.execute_query(query)
    
    def find_travel_expenses(self, min_amount: float = 500, use_chip: bool = True) -> List[Dict[str, Any]]:
        """
        Find transactions related to travel expenses with amount and chip usage filtering
        """
        chip_value = 'TRUE' if use_chip else 'FALSE'
        query = f"""
        SELECT
            t.id AS transaction_id,
            t.amount,
            t.date,
            t.merchant_city,
            t.merchant_state,
            t.use_chip,
            t.client_id
        FROM
            transaction_kb AS t
        WHERE
            content LIKE 'travel expenses' AND   
            t.amount > {min_amount} AND                   
            t.use_chip = {chip_value};
        """
        return self.execute_query(query)
    
    def find_online_shopping(self, state: str = 'California') -> List[Dict[str, Any]]:
        """
        Find transactions for online shopping in a specific state
        """
        query = f"""
        SELECT
            t.id AS transaction_id,
            t.amount,
            t.merchant_city,
            t.merchant_state,
            t.client_id
        FROM
            transaction_kb AS t
        WHERE
            content LIKE 'online shopping' AND
            t.merchant_state = '{state}';
        """
        return self.execute_query(query)
    
    def find_suspicious_transactions(self) -> List[Dict[str, Any]]:
        """
        Find suspicious transactions and get AI-generated summaries
        """
        query = """
        SELECT
            t.id AS transaction_id,
            t.amount,
            t.date,
            t.merchant_city,
            t.merchant_state,
            t.use_chip,
            t.client_id,
            s.summary
        FROM
            transaction_kb AS t
        JOIN
            summarize_transactions_model AS s
        ON
            t.id IS NOT NULL 
        WHERE
            t.content LIKE 'suspicious activity' AND 
            s.transaction_details = CONCAT(
                'Transaction ID: ', t.id,
                ', Amount: ', t.amount,
                ', Date: ', t.date,
                ', Merchant: ', t.merchant_city, ', ', t.merchant_state,
                ', Used Chip: ', t.use_chip
            );
        """
        return self.execute_query(query)
    
    def find_unusual_spending(self) -> List[Dict[str, Any]]:
        """
        Find unusual large spending patterns with AI summaries
        """
        query = """
        SELECT
            t.id AS transaction_id,
            t.amount,
            t.date,
            t.merchant_city,
            t.merchant_state,
            t.use_chip,
            t.client_id,
            s.summary
        FROM
            transaction_kb AS t
        JOIN
            summarize_transactions_model AS s ON 1=1
        WHERE
            t.content LIKE 'unusual large spending' AND
            s.transaction_details = CONCAT(
                'Transaction ID: ', t.id,
                ', Amount: $', t.amount,
                ', Date: ', t.date,
                ', Merchant City: ', t.merchant_city,
                ', Merchant State: ', t.merchant_state,
                ', Used Chip: ', t.use_chip,
                ', Client ID: ', t.client_id
            );
        """
        return self.execute_query(query)
    
    def get_knowledge_base_stats(self) -> Dict[str, int]:
        """
        Get statistics about the knowledge bases
        """
        try:
            client_count = self.execute_query("SELECT count(*) as count FROM client_kb;")
            transaction_count = self.execute_query("SELECT count(*) as count FROM transaction_kb;")
            
            return {
                'client_kb_count': client_count[0]['count'] if client_count else 0,
                'transaction_kb_count': transaction_count[0]['count'] if transaction_count else 0
            }
        except Exception as e:
            print(f"Error getting knowledge base stats: {e}")
            return {'client_kb_count': 0, 'transaction_kb_count': 0}
    
    def custom_semantic_search(self, 
                             search_term: str, 
                             kb_type: str = 'transaction',
                             filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Perform custom semantic search on knowledge bases
        
        Args:
            search_term: Natural language search term
            kb_type: 'transaction' or 'client'
            filters: Dictionary of filters to apply
            
        Returns:
            List of matching results
        """
        kb_name = f"{kb_type}_kb"
        
        # Build the base query
        query = f"SELECT * FROM {kb_name} WHERE content LIKE '{search_term}'"
        
        # Add filters if provided
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    filter_conditions.append(f"{kb_name}.{key} = '{value}'")
                else:
                    filter_conditions.append(f"{kb_name}.{key} = {value}")
            
            if filter_conditions:
                query += " AND " + " AND ".join(filter_conditions)
        
        query += ";"
        return self.execute_query(query)
    
    def test_connection(self) -> bool:
        """
        Test if MindsDB connection is working
        """
        try:
            if not self.connection:
                return False
            
            # Try a simple query
            result = self.execute_query("SELECT 1 as test;")
            return len(result) > 0 and result[0].get('test') == 1
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


# Global instance for easy access
mindsdb_util = MindsDBUtil()