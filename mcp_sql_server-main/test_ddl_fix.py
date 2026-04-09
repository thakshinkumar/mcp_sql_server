"""Test script to verify DDL statements return success correctly."""

import requests
import json

API_URL = "http://localhost:8000/api/query/text"

def test_query(query_text, description):
    """Test a single query."""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Query: {query_text}")
    
    response = requests.post(
        API_URL,
        json={"query": query_text}
    )
    
    result = response.json()
    
    print(f"\nSuccess: {result['success']}")
    print(f"Selected SQL: {result['selected_sql']}")
    
    if result['result']:
        print(f"Result: {result['result']}")
    
    if result['error']:
        print(f"Error: {result['error']}")
    
    print(f"\nMetrics:")
    print(f"  - Execution time: {result['metrics']['execution_time_ms']:.2f} ms")
    print(f"  - Rows affected: {result['metrics']['rows_affected']}")
    print(f"  - Success: {result['metrics']['success']}")
    
    return result['success']

if __name__ == "__main__":
    print("Testing DDL Statement Success Handling")
    print("Make sure the API server is running: python run_api.py")
    
    tests = [
        ("Create a table called TestTable with id and name columns", "CREATE TABLE"),
        ("Add email column to TestTable", "ALTER TABLE - ADD COLUMN"),
        ("List all tables", "SELECT - List Tables"),
        ("Show me all data from TestTable", "SELECT - Query Table"),
        ("Drop the TestTable table", "DROP TABLE"),
    ]
    
    results = []
    for query, desc in tests:
        try:
            success = test_query(query, desc)
            results.append((desc, success))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append((desc, False))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for desc, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {desc}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
