"""Simple test for CREATE TABLE success response."""

import requests
import json

API_URL = "http://localhost:8000/api/query/text"

def test_create_table():
    """Test CREATE TABLE returns success."""
    
    # First, clean up
    print("Step 1: Cleaning up any existing 'TestUser' table...")
    response = requests.post(API_URL, json={"query": "Drop the TestUser table"})
    print(f"Cleanup result: {response.json().get('success', 'N/A')}")
    
    print("\n" + "="*60)
    print("Step 2: Creating new table 'TestUser'...")
    print("="*60)
    
    response = requests.post(
        API_URL,
        json={"query": "Create a table called TestUser with id and username columns"}
    )
    
    result = response.json()
    
    print(f"\nAPI Response:")
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)
    
    print(f"\n1. Success field: {result['success']}")
    print(f"2. Metrics success: {result['metrics']['success']}")
    print(f"3. Has result: {result['result'] is not None}")
    print(f"4. Has error: {result['error'] is not None}")
    
    if result['result']:
        print(f"5. Result message: {result['result'].get('message', 'N/A')}")
    
    if result['error']:
        print(f"6. Error message: {result['error']}")
    
    print("\n" + "="*60)
    if result['success'] and result['result'] and not result['error']:
        print("✓ TEST PASSED - CREATE TABLE returns success correctly!")
    else:
        print("✗ TEST FAILED - Still showing error or no result")
        print("\nExpected:")
        print("  - success: true")
        print("  - result: {message: '...'}") 
        print("  - error: null")
        print("\nActual:")
        print(f"  - success: {result['success']}")
        print(f"  - result: {result['result']}")
        print(f"  - error: {result['error']}")
    print("="*60)

if __name__ == "__main__":
    print("Testing CREATE TABLE Success Response")
    print("Make sure API server is running: python run_api.py\n")
    
    try:
        test_create_table()
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to API server!")
        print("Make sure it's running: python run_api.py")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
