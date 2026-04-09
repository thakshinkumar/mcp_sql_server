"""Test that caching is removed."""
import requests

# Test same query twice - should NOT be cached
for i in range(2):
    print(f"\nRequest {i+1}:")
    response = requests.post(
        "http://localhost:8000/api/query/text",
        json={"query": "List all tables in my database"}
    )
    result = response.json()
    
    print(f"  Success: {result['success']}")
    print(f"  Has 'cached' field: {'cached' in result}")
    print(f"  Candidates: {len(result['candidates'])}")
    
print("\n✓ Caching removed successfully!" if 'cached' not in result else "\n✗ Cache still present")
