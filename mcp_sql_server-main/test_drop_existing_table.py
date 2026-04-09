"""Test dropping a table that actually exists."""
import requests

# First, create a test table
print("1. Creating TestTable...")
response = requests.post(
    "http://localhost:8000/api/query/text",
    json={"query": "Create a table called TestTable with id and name"}
)
result = response.json()
print(f"   Create result: {result['success']}")
if not result['success'] and 'already' in str(result.get('error', '')):
    print("   (Table already exists)")

# Now drop it
print("\n2. Dropping TestTable...")
response = requests.post(
    "http://localhost:8000/api/query/text",
    json={"query": "Delete the TestTable table"}
)
result = response.json()
print(f"   Drop result: {result['success']}")
print(f"   SQL: {result['selected_sql']}")

if result['success']:
    print("\n✓ Table dropped successfully! You have permission.")
else:
    print(f"\n✗ Error: {result.get('error')}")
