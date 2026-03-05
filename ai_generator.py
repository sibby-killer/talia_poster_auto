import os
import requests
import random
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# Predefined aesthetics to make the AI prompt highly realistic and engaging

# SFW everyday aesthetics — naturally attractive, real clothing, Pinterest/Instagram style
FEMALE_PROMPTS = [
    "Full body shot of a beautiful young woman wearing fitted high-waist jeans and a crop top, golden hour outdoor lighting, natural hair, smiling, standing on a city street, candid and natural, not animated, real person, photorealistic",
    "Full body photo of a gorgeous curvy woman in a flowy summer dress, outdoor cafe setting, warm sunlight, natural smile, Instagram-worthy but real and candid, photorealistic, not AI generated",
    "Full body image of a pretty young woman in tight gym leggings and a fitted sports bra, at a park, natural lighting, authentic and real, photorealistic, confident posture, not animated",
    "Full body portrait of a beautiful woman wearing stylish jean shorts and a simple fitted top, beach background, golden hour, candid real photo, not animated, photorealistic, real skin texture",
    "Full body photo of an attractive young woman in a bodycon dress at a rooftop party, city lights, natural makeup, candid real photo, photorealistic, Instagram aesthetic, not animated",
]

MALE_PROMPTS = [
    "Full body shot of a handsome fit young man in fashionable streetwear — joggers and a fitted t-shirt, city street background, natural confident pose, candid real photo, photorealistic, not animated",
    "Full body portrait of a good-looking man in slim-fit jeans and a casual polo shirt, golden hour outdoor lighting, natural and authentic, photorealistic, real skin texture, not animated",
    "Full body photo of a tall attractive man in basketball shorts and a muscle tee, at a park, natural lighting, casual and confident, real and candid, photorealistic, not animated",
    "Full body image of a stylish handsome man wearing chinos and a button-up shirt, outdoor cafe, warm sunlight, authentic candid photo, photorealistic, not animated",
    "Full body photo of a handsome muscular man in fitted jeans and a plain white tee, urban street background, natural lighting, real and candid, photorealistic, not animated",
]

def generate_ai_image(gender="female"):
    """
    Generates an image using Hugging Face (FLUX.1) first.
    If it fails, falls back to Pollinations.ai.
    Returns the URL/File path of the generated image.
    """
    hf_token = os.environ.get("HF_API_TOKEN")
    
    # Pick a random SFW prompt based on gender
    if gender == "female":
        prompt = random.choice(FEMALE_PROMPTS)
    else:
        prompt = random.choice(MALE_PROMPTS)
    
    # Try Hugging Face first (Primary)
    if hf_token and hf_token != "your_huggingface_token":
        result = _try_huggingface(prompt, hf_token)
        if result:
            return result
    
    # Fallback to Pollinations
    print("Falling back to Pollinations.ai...")
    return _try_pollinations(prompt)


def _try_huggingface(prompt, token):
    # Updated to the correct serverless inference routing URL
    url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Negative prompt to prevent morphed/weird AI artifacts
    negative = "deformed, mutated, extra limbs, extra hands, extra fingers, fused fingers, bad anatomy, distorted face, ugly, cartoon, animated, 3d render, painting, drawing, sketch, watermark, blurry, low quality, nsfw, nude, morphed, warped, disfigured, out of frame, cropped, worst quality"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative,
            "num_inference_steps": 4,
            "guidance_scale": 3.5,
            "width": 768,
            "height": 1024
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            filename = f"static/ai_gen_{os.urandom(4).hex()}.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print(f"HF API Failed: {response.text}")
    except Exception as e:
        print(f"HF Exception: {e}")
    return None

def _try_pollinations(prompt):
    encoded_prompt = urllib.parse.quote(prompt)
    # Add a random seed so it bypasses cache
    seed = random.randint(1, 100000)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&nologo=true"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        if response.status_code == 200:
            filename = f"static/ai_gen_{os.urandom(4).hex()}.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print(f"Pollinations Failed: {response.status_code}")
    except Exception as e:
        print(f"Pollinations Exception: {e}")
    
    return None
