#!/usr/bin/env python
"""Quick test of API query endpoint."""

import requests
import json

def test_query(query_text):
    """Test a query via API."""
    url = "http://localhost:8000/api/query/text"
    headers = {"Content-Type": "application/json"}
    data = {"query": query_text}
    
    print(f"\n{'='*60}")
    print(f"Testing: {query_text}")
    print('='*60)
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('candidates'):
            print(f"\nCandidates ({len(result['candidates'])}):")
            for i, sql in enumerate(result['candidates'], 1):
                print(f"  {i}. {sql[:80]}...")
        
        if result.get('selected_sql'):
            print(f"\nSelected SQL:")
            print(f"  {result['selected_sql'][:100]}...")
        
        if result.get('error'):
            print(f"\n❌ Error: {result['error'][:200]}")
        else:
            print(f"\n✅ Success!")
            if result.get('result'):
                res = result['result']
                if isinstance(res, dict) and 'rows' in res:
                    print(f"   Rows returned: {len(res['rows'])}")
                    if res['rows']:
                        print(f"   First row: {res['rows'][0]}")
        
        print(f"\nMetrics:")
        metrics = result.get('metrics', {})
        print(f"  Execution time: {metrics.get('execution_time_ms', 0):.2f} ms")
        print(f"  Cached: {result.get('cached', False)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API. Is it running?")
        print("   Run: python run_api.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  API QUERY TESTER")
    print("="*60)
    print("\nMake sure API is running: python run_api.py")
    print("Press Ctrl+C to stop\n")
    
    # Test queries
    queries = [
        "List all tables in my database",
        "Show me the SQL Server version",
        "List all tables in my database",  # Test cache
    ]
    
    for query in queries:
        test_query(query)
        input("\nPress Enter for next test...")
    
    print("\n" + "="*60)
    print("  TESTS COMPLETE")
    print("="*60 + "\n")
