"""List all tables to see what exists."""
import requests

response = requests.post(
    "http://localhost:8000/api/query/text",
    json={"query": "List all tables in my database"}
)

result = response.json()

print("Tables in database:")
print("="*50)
if result['result'] and result['result']['rows']:
    for row in result['result']['rows']:
        print(f"  - {row[0]}")
else:
    print("  No tables found")
