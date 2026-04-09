"""Test Orders table creation."""
import requests

response = requests.post(
    "http://localhost:8000/api/query/text",
    json={"query": "Create a table called Orders with orderId and customerName as attributes"}
)

result = response.json()

print("SQL Generated:")
print(result['selected_sql'])
print(f"\nSuccess: {result['success']}")
if not result['success']:
    print(f"Error: {result.get('error')}")
