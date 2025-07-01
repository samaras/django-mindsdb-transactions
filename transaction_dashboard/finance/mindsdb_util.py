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
        Find clients in wealthy areas with age and income filtering
        
        Note: This assumes your client_kb has columns: id, address, current_age, per_capita_income, gender
        You may need to adjust based on your actual KB schema
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
            c.current_age > {min_age} AND                    
            c.per_capita_income > {min_income};
        """
        return self.execute_query(query)
    
    def find_travel_expenses(self, min_amount: float = 500, use_chip: bool = True) -> List[Dict[str, Any]]:
        """
        Find transactions related to travel with amount and chip usage filtering
        
        Note: This assumes your transaction_kb has appropriate columns
        """
        # Use proper boolean value for MindsDB
        chip_value = 'true' if use_chip else 'false'
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
            t.merchant_state = '{state}';
        """
        return self.execute_query(query)
    
    def semantic_search_transactions(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Perform semantic search on transaction knowledge base
        
        Args:
            search_term: Natural language search term (e.g., "suspicious activity", "travel expenses")
            limit: Maximum number of results to return
        """
        query = f"""
        SELECT 
            *
        FROM transaction_kb 
        WHERE 
            MATCH('{search_term}')
        LIMIT {limit};
        """
        return self.execute_query(query)
    
    def semantic_search_clients(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Perform semantic search on client knowledge base
        
        Args:
            search_term: Natural language search term (e.g., "wealthy suburban areas")
            limit: Maximum number of results to return
        """
        query = f"""
        SELECT 
            *
        FROM client_kb 
        WHERE 
            MATCH('{search_term}')
        LIMIT {limit};
        """
        return self.execute_query(query)
    
    def get_transaction_summary(self, transaction_id: int) -> List[Dict[str, Any]]:
        """
        Get AI-generated summary for a specific transaction
        
        Note: This assumes you have a model named 'summarize_transactions_model'
        and that the model expects transaction_id as input
        """
        query = f"""
        SELECT 
            transaction_id,
            summary
        FROM summarize_transactions_model 
        WHERE 
            transaction_id = {transaction_id};
        """
        return self.execute_query(query)
    
    def analyze_suspicious_patterns(self, client_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Use AI model to analyze suspicious transaction patterns
        
        This is a more realistic approach than the original join-based method
        """
        where_clause = f"WHERE client_id = {client_id}" if client_id else ""
        
        query = f"""
        SELECT 
            t.id,
            t.amount,
            t.date,
            t.merchant_city,
            t.merchant_state,
            t.client_id,
            p.risk_score,
            p.risk_reason
        FROM transaction_kb t
        JOIN pattern_analysis_model p ON t.id = p.transaction_id
        {where_clause}
        ORDER BY p.risk_score DESC;
        """
        return self.execute_query(query)
    
    def get_knowledge_base_stats(self) -> Dict[str, int]:
        """
        Get statistics about the knowledge bases
        """
        try:
            client_count = self.execute_query("SELECT COUNT(*) as count FROM client_kb;")
            transaction_count = self.execute_query("SELECT COUNT(*) as count FROM transaction_kb;")
            
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
                             filters: Dict[str, Any] = None,
                             limit: int = 10) -> List[Dict[str, Any]]:
        """
        Perform custom semantic search on knowledge bases with optional filters
        
        Args:
            search_term: Natural language search term
            kb_type: 'transaction' or 'client'
            filters: Dictionary of filters to apply
            limit: Maximum number of results
            
        Returns:
            List of matching results
        """
        kb_name = f"{kb_type}_kb"
        
        # Build the base semantic search query
        query = f"SELECT * FROM {kb_name} WHERE MATCH('{search_term}')"
        
        # Add filters if provided
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    # Escape single quotes in string values
                    escaped_value = value.replace("'", "''")
                    filter_conditions.append(f"{key} = '{escaped_value}'")
                elif isinstance(value, bool):
                    filter_conditions.append(f"{key} = {'true' if value else 'false'}")
                else:
                    filter_conditions.append(f"{key} = {value}")
            
            if filter_conditions:
                query += " AND " + " AND ".join(filter_conditions)
        
        query += f" LIMIT {limit};"
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
    
    def list_available_tables(self) -> List[str]:
        """
        List all available tables/knowledge bases in MindsDB
        """
        try:
            result = self.execute_query("SHOW TABLES;")
            return [row.get('table_name', row.get('Tables_in_mindsdb', '')) for row in result]
        except Exception as e:
            print(f"Error listing tables: {e}")
            return []
    
    def describe_table(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get schema information for a specific table
        """
        try:
            return self.execute_query(f"DESCRIBE {table_name};")
        except Exception as e:
            print(f"Error describing table {table_name}: {e}")
            return []


# Global instance for easy access
mindsdb_util = MindsDBUtil()