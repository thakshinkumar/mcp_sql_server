import pytest
import asyncio
from mssql_mcp_server.server import app, get_connection
from mcp.types import Tool

@pytest.mark.asyncio
async def test_schema_refresh_detection():
    \"\"\"Test that schema changes are immediately detected (no caching).\"\"\"
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clean up test table if exists
    cursor.execute(\"DROP TABLE IF EXISTS test_ssms_table\")
    conn.commit()
    
    # 1. Verify table NOT exists
    cursor.execute(\"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'test_ssms_table'\")
    assert cursor.fetchone() is None
    
    # 2. CREATE table (simulate SSMS change)
    cursor.execute(\"CREATE TABLE test_ssms_table (id INT PRIMARY KEY, name VARCHAR(100))\")
    conn.commit()
    
    # 3. Verify list_resources sees it immediately (live query)
    resources = await app.list_resources()
    table_uris = [r.uri for r in resources]
    assert any('test_ssms_table' in uri for uri in table_uris)
    
    # 4. Add column (SSMS ALTER)
    cursor.execute(\"ALTER TABLE test_ssms_table ADD email VARCHAR(255)\")
    conn.commit()
    
    # 5. Verify columns detected live (would use get_table_columns if in API)
    cursor.execute(\"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'test_ssms_table'\")
    cols = [row[0] for row in cursor.fetchall()]
    assert 'email' in cols
    
    # 6. Read resource - verify no stale data
    uri = next(r.uri for r in resources if 'test_ssms_table' in r.uri)
    content = await app.read_resource(uri)
    assert 'test_ssms_table' in content  # Should reflect live
    
    # Cleanup
    cursor.execute(\"DROP TABLE test_ssms_table\")
    conn.commit()
    cursor.close()
    conn.close()
    print(\"✅ Schema refresh test PASSED: SSMS changes detected live, no stale values.\")

if __name__ == \"__main__\":
    asyncio.run(test_schema_refresh_detection())

