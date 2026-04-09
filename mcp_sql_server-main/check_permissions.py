"""Check current SQL Server permissions and provide guidance."""

import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

def check_permissions():
    """Check current user and permissions."""
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
        
        print("=" * 60)
        print("SQL SERVER PERMISSION CHECK")
        print("=" * 60)
        
        # Get current user
        cursor.execute("SELECT SYSTEM_USER AS CurrentUser, USER_NAME() AS DatabaseUser")
        user_info = cursor.fetchone()
        print(f"\n1. Current Windows User: {user_info[0]}")
        print(f"   Database User: {user_info[1]}")
        
        # Get database roles
        cursor.execute("""
            SELECT r.name AS RoleName
            FROM sys.database_principals r
            INNER JOIN sys.database_role_members m ON r.principal_id = m.role_principal_id
            INNER JOIN sys.database_principals u ON m.member_principal_id = u.principal_id
            WHERE u.name = USER_NAME()
        """)
        roles = cursor.fetchall()
        print(f"\n2. Database Roles:")
        if roles:
            for role in roles:
                print(f"   - {role[0]}")
        else:
            print("   - No roles assigned")
        
        # Get specific permissions
        cursor.execute("SELECT * FROM fn_my_permissions(NULL, 'DATABASE')")
        permissions = cursor.fetchall()
        print(f"\n3. Database Permissions:")
        
        has_create = False
        has_alter = False
        has_drop = False
        
        for perm in permissions:
            perm_name = perm[3]  # permission_name column
            if 'CREATE' in perm_name:
                has_create = True
                print(f"   ✓ {perm_name}")
            elif 'ALTER' in perm_name:
                has_alter = True
                print(f"   ✓ {perm_name}")
            elif 'DROP' in perm_name or 'CONTROL' in perm_name:
                has_drop = True
                print(f"   ✓ {perm_name}")
        
        print("\n" + "=" * 60)
        print("PERMISSION ANALYSIS")
        print("=" * 60)
        
        print(f"\nCREATE TABLE: {'✓ Allowed' if has_create else '✗ Not allowed'}")
        print(f"ALTER TABLE:  {'✓ Allowed' if has_alter else '✗ Not allowed'}")
        print(f"DROP TABLE:   {'✓ Allowed' if has_drop else '✗ Not allowed'}")
        
        if not (has_create and has_alter and has_drop):
            print("\n" + "=" * 60)
            print("HOW TO FIX PERMISSIONS")
            print("=" * 60)
            print("\nYou need to grant permissions. Run these steps:")
            print("\n1. Open SQL Server Management Studio (SSMS)")
            print("2. Connect as Administrator (sa or sysadmin)")
            print("3. Open a New Query window")
            print("4. Run this command (replace with your username):")
            print(f"\n   EXEC sp_addrolemember 'db_ddladmin', '{user_info[0]}';\n")
            print("5. Alternatively, run the grant_permissions.sql script")
            print("\nOR use a different database (not 'master'):")
            print("\n   1. Create a new database: CREATE DATABASE TestDB;")
            print("   2. Update .env file: MSSQL_DATABASE=TestDB")
            print("   3. Restart the API server")
        else:
            print("\n✓ All required permissions are granted!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n✗ Error checking permissions: {e}")
        print("\nMake sure SQL Server is running and accessible.")

if __name__ == "__main__":
    check_permissions()
