import os
import random
from apscheduler.schedulers.background import BackgroundScheduler
from ai_generator import generate_ai_image
from fb_poster import post_to_facebook
from supabase_client import get_supabase
from dotenv import load_dotenv

load_dotenv()

# US-targeted captions and hashtags (targeting EST prime-time audience)
CAPTIONS = [
    "✨ Vibes of the day! Real people, real connections. Are you looking for your perfect match or just new friends? Drop a comment! 💬\n\n#community #connect #vibes #singlelife #nyc #losangeles #dating #meetup #talia #usa",
    "🌟 Beauty is everywhere! This vibe is brought to you by our community. Want to be featured? Link in comments! ❤️\n\n#aesthetic #beauty #singleinamerica #community #americangirl #talia #blackgirlmagic #latinas",
    "💫 New day, new vibes. Whether you're looking for friendship or love — this is the place! 😍\n\n#connect #singleandready #americandating #community #talia #love #nyclife #californiadreaming",
    "🔥 Looking good today! Our community is growing — join us and find your people! 🙌\n\n#community #lifestyle #friends #singlelife #talia #usadating #blacklove #melanin #girls",
    "✨ Every day is a good day to make new connections! 🌎💕\n\n#vibes #connect #community #talia #meetup #friendship #americanlife #datingapp #usa #nyc",
    "🌸 Real people, real connections. Want to be featured on our page? Click the link in comments!\n\n#featured #community #aesthetic #talia #singleinamerica #usagirls #blackgirlmagic #melanin",
]

def run_ai_job():
    print("Running scheduled AI Generation Job...")
    supabase = get_supabase()
    
    # 1. Pick a random gender (mostly female, some male)
    gender = random.choice(["female", "female", "female", "female", "male", "male"])
    
    # 2. Generate image locally
    image_path = generate_ai_image(gender)
    if not image_path:
        print("Failed to generate image. Skipping this job.")
        return
        
    print(f"Image generated: {image_path}")
    
    # 3. Upload to Supabase Storage to get a public URL
    public_url = None
    if supabase:
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            unique_path = f"ai_generated/{os.urandom(8).hex()}.jpg"
            supabase.storage.from_("submissions").upload(
                file=image_bytes,
                path=unique_path,
                file_options={"content-type": "image/jpeg"}
            )
            public_url = supabase.storage.from_("submissions").get_public_url(unique_path)
            print(f"Uploaded to Supabase. Public URL: {public_url}")
        except Exception as e:
            print(f"Failed to upload to Supabase: {e}")
    
    # 4. Clean up local file
    try:
        os.remove(image_path)
    except:
        pass
    
    if not public_url:
        print("No public URL available. Cannot post to Facebook. Skipping.")
        return
    
    # 5. Post to Facebook with a random caption
    caption = random.choice(CAPTIONS)
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5000")
    comment = f"Want to be featured or find someone special? Submit your profile here 👉 {render_url}"
    
    fb_link = post_to_facebook(public_url, caption, comment)
    if fb_link:
        print(f"Successfully posted to Facebook: {fb_link}")
    else:
        print("Facebook posting failed.")


def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run 6 times a day (every 4 hours)
    scheduler.add_job(func=run_ai_job, trigger="interval", hours=4)
    scheduler.start()
    print("Background scheduler started (Running every 4 hours)...")

