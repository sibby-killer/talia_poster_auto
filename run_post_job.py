import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from scheduler import run_ai_job

if __name__ == "__main__":
    print("Running one-time AI post job...")
    run_ai_job()
    print("Done.")
