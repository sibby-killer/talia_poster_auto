import os
from supabase import create_client, Client

def get_supabase() -> Client:
    url: str = os.environ.get("SUPABASE_URL", "")
    key: str = os.environ.get("SUPABASE_KEY", "")
    
    # Return None if not configured properly yet
    if not url or not key or url == "your_supabase_project_url":
        print("WARNING: Supabase URL or Key not found. Database features will be disabled.")
        return None
        
    try:
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None
