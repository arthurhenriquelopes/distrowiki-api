import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

# Initialize Supabase client
# Warning: Without valid keys in .env, this will fail at runtime if accessed
try:
    if url and key:
        supabase: Client = create_client(url, key)
    else:
        supabase = None
        print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")
except Exception as e:
    supabase = None
    print(f"Error initializing Supabase client: {e}")

def get_supabase_client() -> Client:
    return supabase
