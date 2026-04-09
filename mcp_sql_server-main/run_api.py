#!/usr/bin/env python
"""Run the FastAPI web server."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    import uvicorn
    from mssql_mcp_server.api.main import app
    
    print("="*60)
    print("Voice-Enabled Self-Optimizing SQL Server")
    print("="*60)
    print("\nStarting FastAPI server...")
    print("API Documentation: http://localhost:8000/docs")
    print("API Root: http://localhost:8000")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
