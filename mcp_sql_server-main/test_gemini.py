#!/usr/bin/env python
"""Test Gemini API connection and NL-to-SQL generation."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_connection():
    """Test Gemini API connection."""
    print("\n" + "="*60)
    print("  GEMINI API CONNECTION TEST")
    print("="*60 + "\n")
    
    # Check configuration
    api_key = os.getenv("LLM_API_KEY", "")
    provider = os.getenv("LLM_PROVIDER", "")
    model = os.getenv("LLM_MODEL", "")
    
    print("Configuration:")
    print(f"  Provider: {provider}")
    print(f"  Model: {model}")
    print(f"  API Key: {'✓ Set' if api_key else '✗ Not set'}")
    
    if not api_key:
        print("\n❌ ERROR: No API key found!")
        print("\nPlease:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Edit .env file and set: LLM_API_KEY=your_key_here")
        print("3. Run this test again")
        return False
    
    print("\n" + "-"*60)
    print("Testing Gemini API connection...")
    print("-"*60 + "\n")
    
    try:
        # Import and configure Gemini
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        print("✓ Gemini library imported")
        print("✓ API key configured")
        
        # Create model
        model_instance = genai.GenerativeModel(model)
        print(f"✓ Model '{model}' initialized")
        
        # Test 1: Simple generation
        print("\n" + "-"*60)
        print("Test 1: Simple Text Generation")
        print("-"*60)
        
        response = model_instance.generate_content("Say 'Hello from Gemini!'")
        print(f"Response: {response.text}")
        print("✓ Basic generation working")
        
        # Test 2: SQL generation
        print("\n" + "-"*60)
        print("Test 2: SQL Query Generation")
        print("-"*60)
        
        prompt = """Convert this natural language to SQL Server syntax:
"List all tables in the database"

Return only the SQL query, no explanation."""
        
        response = model_instance.generate_content(prompt)
        sql = response.text.strip()
        print(f"Generated SQL: {sql}")
        print("✓ SQL generation working")
        
        # Test 3: Multiple candidates
        print("\n" + "-"*60)
        print("Test 3: Multiple SQL Candidates")
        print("-"*60)
        
        prompt = """Generate 3 different SQL Server queries to list all tables.
Use different approaches. Return only SQL queries, one per line."""
        
        response = model_instance.generate_content(prompt)
        print("Generated candidates:")
        for i, line in enumerate(response.text.strip().split('\n'), 1):
            if line.strip():
                print(f"  {i}. {line.strip()}")
        print("✓ Multiple candidates working")
        
        # Success
        print("\n" + "="*60)
        print("  ✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nGemini API is working correctly!")
        print("You can now use it with the POC system.")
        print("\nNext steps:")
        print("  1. Run: python test_poc.py")
        print("  2. Run: python run_api.py")
        print("  3. Try complex queries!")
        print("\n")
        
        return True
        
    except ImportError:
        print("\n❌ ERROR: google-generativeai library not installed!")
        print("\nPlease run:")
        print("  pip install google-generativeai")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPossible issues:")
        print("  1. Invalid API key")
        print("  2. Network connection problem")
        print("  3. API quota exceeded")
        print("  4. Model name incorrect")
        print("\nPlease check your configuration and try again.")
        return False


if __name__ == "__main__":
    success = test_gemini_connection()
    sys.exit(0 if success else 1)
