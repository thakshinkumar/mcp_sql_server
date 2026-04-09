import sys

print(sys.path)

try:
    import mssql_mcp_server
    print("ok")
    print(getattr(mssql_mcp_server, "__all__", None))
except Exception as exc:
    print(type(exc).__name__)
    print(str(exc))
    raise
