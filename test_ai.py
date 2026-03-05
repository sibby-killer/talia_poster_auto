import os
from dotenv import load_dotenv
from ai_generator import generate_ai_image

load_dotenv()

print("Testing AI Generator Pipeline with new highly realistic full-body prompts...")
try:
    result = generate_ai_image("female")
    if result:
        print(f"✅ SUCCESS. Image saved as: {result}")
        # Rename it to make it easy to find
        os.rename(result, "static/hf_test_girl_new.jpg")
        print("Moved to static/hf_test_girl_new.jpg")
    else:
        print("❌ FAILED. No image returned.")
except Exception as e:
    print(f"Error: {e}")
