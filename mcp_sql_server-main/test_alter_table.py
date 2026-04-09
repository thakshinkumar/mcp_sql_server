"""Test ALTER TABLE query."""
import requests
import json

response = requests.post(
    "http://localhost:8000/api/query/text",
    json={"query": "Add email id column in customer table"}
)

result = response.json()

print("="*70)
print("SQL CANDIDATES:")
print("="*70)
for i, sql in enumerate(result['candidates'], 1):
    print(f"{i}. {sql}")

print("\n" + "="*70)
print("SELECTED SQL:")
print("="*70)
print(result['selected_sql'])

if result['success']:
    print("\n✓ Query executed successfully!")
else:
    print(f"\n✗ Query failed: {result.get('error')}")
