"""Test Products table creation."""
import requests

response = requests.post(
    "http://localhost:8000/api/query/text",
    json={"query": "Create a table called 'Products' with productId and name as attributes"}
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
    print("\n✓ Table created successfully!")
else:
    print(f"\n✗ Error: {result.get('error')}")
