"""Test OpenAI/Portkey integration with the API."""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_query(query_text):
    """Test a natural language query."""
    print(f"\n{'='*60}")
    print(f"Testing: {query_text}")
    print('='*60)
    
    response = requests.post(
        f"{BASE_URL}/api/query/text",
        json={"query": query_text},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Success: {result['success']}")
        print(f"✓ Input: {result['input']}")
        print(f"\n✓ Generated SQL Candidates ({len(result['candidates'])}):")
        for i, sql in enumerate(result['candidates'], 1):
            print(f"  {i}. {sql}")
        print(f"\n✓ Selected SQL: {result['selected_sql']}")
        
        if result['result']:
            print(f"\n✓ Result:")
            print(f"  Columns: {result['result']['columns']}")
            print(f"  Rows: {len(result['result']['rows'])} rows")
            if result['result']['rows']:
                print(f"  Sample: {result['result']['rows'][:3]}")
        
        print(f"\n✓ Metrics:")
        print(f"  Execution Time: {result['metrics'].get('execution_time_ms', 0):.2f} ms")
        print(f"  Cached: {result['cached']}")
        
        if result.get('error'):
            print(f"\n✗ Error: {result['error']}")
    else:
        print(f"\n✗ HTTP Error: {response.status_code}")
        print(f"✗ Response: {response.text}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("OpenAI/Portkey Integration Test")
    print("="*60)
    print("\nThis will test if GPT-4 is generating SQL queries")
    print("via Portkey endpoint: https://api.portkey.ai/v1")
    print("\nWatch for SQL quality - GPT-4 should generate")
    print("complete, valid SQL queries (not incomplete like Gemini)")
    
    # Test 1: List tables
    test_query("List all tables in my database")
    
    # Test 2: Schema query
    test_query("Show me the schema of the Customers table")
    
    # Test 3: Create table
    test_query("Create a Products table with id, name, price, and stock columns")
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)
    print("\nCheck the SQL candidates above:")
    print("- Should be complete and valid SQL")
    print("- Should have proper syntax (no unclosed quotes)")
    print("- Should have complete WHERE clauses")
    print("\nIf you see incomplete SQL, check the API logs")
    print("="*60 + "\n")
