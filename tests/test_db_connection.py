import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import DATABASE_URL

def test_connection():
    print("--- Testing Database Connection ---")
    print(f"URL: {DATABASE_URL.split('@')[-1]}") # Hide credentials
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connection Successful!")
            print(f"Server Version: {version}")
            return True
    except Exception as e:
        print(f"❌ Connection Failed:")
        print(e)
        return False

if __name__ == "__main__":
    test_connection()
