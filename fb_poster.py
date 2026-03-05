import os
import requests
from dotenv import load_dotenv

load_dotenv()

def post_to_facebook(image_url, message, link_comment=""):
    """
    Posts an image to the Facebook page using the Graph API.
    Expects FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID in .env
    """
    page_id = os.environ.get("FB_PAGE_ID", "")
    page_token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
    
    if not page_id or not page_token:
        print("Facebook API credentials not found.")
        return None

    # Post Image
    post_url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
    payload = {
        "url": image_url,
        "caption": message,
        "access_token": page_token
    }
    
    try:
        response = requests.post(post_url, data=payload).json()
        if "id" in response:
            post_id = response["id"]
            
            # Post the link as a first comment if provided
            if link_comment:
                comment_url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
                requests.post(comment_url, data={
                    "message": link_comment,
                    "access_token": page_token
                })
            
            # Return the public link to the post
            # The ID returned by graph API is usually Format: PAGEID_POSTID
            ids = post_id.split('_')
            if len(ids) == 2:
                return f"https://facebook.com/{ids[0]}/posts/{ids[1]}"
            return f"https://facebook.com/{page_id}/posts/{post_id}"
            
        else:
            print(f"Facebook API Error: {response}")
            return None
    except Exception as e:
        print(f"Facebook Post Exception: {e}")
        return None
