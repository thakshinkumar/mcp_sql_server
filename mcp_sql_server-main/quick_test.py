"""Quick test of the API."""
import requests

response = requests.post(
    "http://localhost:8000/api/query/text",
    json={"query": "List all tables in my database"}
)

print(response.json())
