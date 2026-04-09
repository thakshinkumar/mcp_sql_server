"""Quick demo script for immediate screenshot capture."""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/query/text"

def demo_query(query, description=""):
    """Execute and display a query with formatted output."""
    print("\n" + "="*80)
    if description:
        print(f"📌 {description}")
        print("="*80)
    
    print(f"\n💬 Natural Language Query:")
    print(f'   "{query}"')
    print()
    
    try:
        response = requests.post(API_URL, json={"query": query}, timeout=10)
        result = response.json()
        
        print(f"🤖 Generated SQL Candidates:")
        for i, candidate in enumerate(result.get('candidates', []), 1):
            marker = "→" if candidate == result.get('selected_sql') else " "
            print(f"   {marker} {i}. {candidate}")
        
        print(f"\n✅ Selected & Executed:")
        print(f"   {result.get('selected_sql', 'N/A')}")
        
        metrics = result.get('metrics', {})
        print(f"\n📊 Performance Metrics:")
        print(f"   ⏱️  Execution Time: {metrics.get('execution_time_ms', 0):.2f} ms")
        print(f"   📈 Rows Affected: {metrics.get('rows_affected', 0)}")
        print(f"   ✓  Success: {metrics.get('success', False)}")
        
        if result.get('result'):
            result_data = result.get('result', {})
            print(f"\n📋 Result:")
            
            if 'columns' in result_data and 'rows' in result_data:
                print(f"   Columns: {', '.join(result_data['columns'])}")
                print(f"   Total Rows: {len(result_data['rows'])}")
                
                if result_data['rows']:
                    print(f"\n   Sample Data (first 3 rows):")
                    for i, row in enumerate(result_data['rows'][:3], 1):
                        print(f"   {i}. {row}")
            else:
                print(f"   {result_data.get('message', 'Operation completed')}")
        
        print(f"\n{'─'*80}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"{'─'*80}")
        return False

if __name__ == "__main__":
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "NL-TO-SQL SYSTEM DEMONSTRATION" + " "*28 + "║")
    print("╚" + "="*78 + "╝")
    print(f"\n🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Endpoint: {API_URL}")
    
    # Demo scenarios
    demos = [
        ("List all tables", "Metadata Query - Show Available Tables"),
        ("Create a table called TestDemo with id, name and email", "DDL Operation - Create Table"),
        ("Add phone column to TestDemo table", "DDL Operation - Add Column"),
        ("Insert some dummy data to TestDemo", "DML Operation - Insert Data"),
        ("Show all data from TestDemo", "DQL Operation - Select Data"),
        ("Update TestDemo set name to UpdatedName", "DML Operation - Update Data"),
        ("Remove phone column from TestDemo table", "DDL Operation - Drop Column"),
        ("Drop the TestDemo table", "DDL Operation - Drop Table"),
    ]
    
    print("\n" + "─"*80)
    print("Starting demonstration with 8 different query types...")
    print("─"*80)
    
    success_count = 0
    for query, description in demos:
        if demo_query(query, description):
            success_count += 1
        input("\n⏸️  Press Enter for next query...")
    
    print("\n" + "╔" + "="*78 + "╗")
    print(f"║  DEMONSTRATION COMPLETE: {success_count}/{len(demos)} queries successful" + " "*(78-len(f"  DEMONSTRATION COMPLETE: {success_count}/{len(demos)} queries successful")) + "║")
    print("╚" + "="*78 + "╝\n")
