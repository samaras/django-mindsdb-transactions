#!/usr/bin/env python
"""
Test script for MindsDB functionality
Run this script to test the mindsdb_sdk integration and SQL query execution
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transaction_dashboard.settings')
django.setup()

from finance.mindsdb_util import mindsdb_util

def test_mindsdb_connection():
    """Test the MindsDB connection"""
    print("Testing MindsDB Connection...")
    print("=" * 50)
    
    # Test 1: Connection test
    print("\n1. Testing connection...")
    try:
        connection_status = mindsdb_util.test_connection()
        print(f"Connection status: {'Connected' if connection_status else 'Failed'}")
    except Exception as e:
        print(f"Connection test error: {e}")
    
    # Test 2: Knowledge base stats
    print("\n2. Testing knowledge base stats...")
    try:
        stats = mindsdb_util.get_knowledge_base_stats()
        print(f"Knowledge base stats: {stats}")
    except Exception as e:
        print(f"Stats error: {e}")
    
    print("\n" + "=" * 50)

def test_sql_queries():
    """Test the SQL queries from mindsdb.sql"""
    print("Testing SQL Queries from mindsdb.sql...")
    print("=" * 50)
    
    # Test 1: Wealthy clients query
    print("\n1. Testing wealthy clients query...")
    try:
        results = mindsdb_util.find_wealthy_clients(min_age=35, min_income=60000)
        print(f"Found {len(results)} wealthy clients")
        for result in results[:3]:  # Show first 3
            print(f"  - Client {result.get('client_id')}: Age {result.get('current_age')}, "
                  f"Income ${result.get('per_capita_income')}")
    except Exception as e:
        print(f"Wealthy clients query error: {e}")
    
    # Test 2: Travel expenses query
    print("\n2. Testing travel expenses query...")
    try:
        results = mindsdb_util.find_travel_expenses(min_amount=300, use_chip=True)
        print(f"Found {len(results)} travel expense transactions")
        for result in results[:3]:  # Show first 3
            print(f"  - Transaction {result.get('transaction_id')}: ${result.get('amount')} "
                  f"in {result.get('merchant_city')}")
    except Exception as e:
        print(f"Travel expenses query error: {e}")
    
    # Test 3: Online shopping query
    print("\n3. Testing online shopping query...")
    try:
        results = mindsdb_util.find_online_shopping(state='California')
        print(f"Found {len(results)} online shopping transactions in California")
        for result in results[:3]:  # Show first 3
            print(f"  - Transaction {result.get('transaction_id')}: ${result.get('amount')} "
                  f"in {result.get('merchant_city')}")
    except Exception as e:
        print(f"Online shopping query error: {e}")
    
    # Test 4: Suspicious transactions query
    print("\n4. Testing suspicious transactions query...")
    try:
        results = mindsdb_util.find_suspicious_transactions()
        print(f"Found {len(results)} suspicious transactions")
        for result in results[:3]:  # Show first 3
            print(f"  - Transaction {result.get('transaction_id')}: ${result.get('amount')}")
            if result.get('summary'):
                print(f"    Summary: {result.get('summary')[:100]}...")
    except Exception as e:
        print(f"Suspicious transactions query error: {e}")
    
    # Test 5: Unusual spending query
    print("\n5. Testing unusual spending query...")
    try:
        results = mindsdb_util.find_unusual_spending()
        print(f"Found {len(results)} unusual spending transactions")
        for result in results[:3]:  # Show first 3
            print(f"  - Transaction {result.get('transaction_id')}: ${result.get('amount')}")
            if result.get('summary'):
                print(f"    Summary: {result.get('summary')[:100]}...")
    except Exception as e:
        print(f"Unusual spending query error: {e}")
    
    print("\n" + "=" * 50)

def test_custom_search():
    """Test custom semantic search functionality"""
    print("Testing Custom Semantic Search...")
    print("=" * 50)
    
    # Test 1: Custom transaction search
    print("\n1. Testing custom transaction search...")
    try:
        results = mindsdb_util.custom_semantic_search(
            search_term="high value purchases",
            kb_type="transaction",
            filters={"amount": 1000}
        )
        print(f"Found {len(results)} high value transactions")
    except Exception as e:
        print(f"Custom transaction search error: {e}")
    
    # Test 2: Custom client search
    print("\n2. Testing custom client search...")
    try:
        results = mindsdb_util.custom_semantic_search(
            search_term="young professionals",
            kb_type="client",
            filters={"current_age": 30}
        )
        print(f"Found {len(results)} young professional clients")
    except Exception as e:
        print(f"Custom client search error: {e}")
    
    print("\n" + "=" * 50)

def test_custom_query():
    """Test custom SQL query execution"""
    print("Testing Custom SQL Query Execution...")
    print("=" * 50)
    
    # Test 1: Simple query
    print("\n1. Testing simple query...")
    try:
        results = mindsdb_util.execute_query("SELECT count(*) as count FROM client_kb;")
        print(f"Query result: {results}")
    except Exception as e:
        print(f"Simple query error: {e}")
    
    # Test 2: Complex query
    print("\n2. Testing complex query...")
    try:
        query = """
        SELECT 
            t.id as transaction_id,
            t.amount,
            t.merchant_city,
            c.current_age
        FROM transaction_kb t
        JOIN client_kb c ON t.client_id = c.id
        WHERE t.amount > 500
        LIMIT 5;
        """
        results = mindsdb_util.execute_query(query)
        print(f"Found {len(results)} high-value transactions with client info")
        for result in results[:3]:
            print(f"  - Transaction {result.get('transaction_id')}: ${result.get('amount')} "
                  f"by client age {result.get('current_age')}")
    except Exception as e:
        print(f"Complex query error: {e}")
    
    print("\n" + "=" * 50)

def main():
    """Run all tests"""
    print("MindsDB Integration Test Suite")
    print("=" * 60)
    
    test_mindsdb_connection()
    test_sql_queries()
    test_custom_search()
    test_custom_query()
    
    print("\nTest suite completed!")

if __name__ == "__main__":
    main() 