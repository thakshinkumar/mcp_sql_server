"""Clean up test tables before testing."""

import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

def cleanup_tables():
    """Drop all test tables."""
    try:
        # Connect to SQL Server
        conn = pymssql.connect(
            server=f"{os.getenv('MSSQL_SERVER')}:{os.getenv('MSSQL_PORT')}",
            database=os.getenv('MSSQL_DATABASE'),
            user=None,  # Windows Auth
            password=None,
            tds_version='7.0'
        )
        
        cursor = conn.cursor()
        
        # List of test tables to drop
        test_tables = [
            'Praveen', 'Mobile', 'Products', 'TestTable', 
            'Student', 'Employee'
        ]
        
        print("Cleaning up test tables...")
        print("=" * 60)
        
        for table in test_tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                conn.commit()
                print(f"✓ Dropped table: {table}")
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print(f"  Table {table} doesn't exist (OK)")
                else:
                    print(f"✗ Error dropping {table}: {e}")
        
        print("=" * 60)
        print("Cleanup complete!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    cleanup_tables()
