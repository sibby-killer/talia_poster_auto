import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("TALIA AUTO-POSTER — Starting job...")
print(f"SUPABASE_URL set: {bool(os.environ.get('SUPABASE_URL'))}")
print(f"SUPABASE_KEY set: {bool(os.environ.get('SUPABASE_KEY'))}")
print(f"HF_API_TOKEN set: {bool(os.environ.get('HF_API_TOKEN'))}")
print(f"FB_PAGE_ID set: {bool(os.environ.get('FB_PAGE_ID'))}")
print(f"FB_PAGE_ACCESS_TOKEN set: {bool(os.environ.get('FB_PAGE_ACCESS_TOKEN'))}")
print("=" * 50)

from scheduler import run_ai_job

if __name__ == "__main__":
    run_ai_job()
    print("Job complete.")

