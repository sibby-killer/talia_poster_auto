import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_notification(text, photo_url=None, inline_keyboard=None):
    """
    Sends a message to the Admin Chat ID
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("ADMIN_CHAT_ID")
    
    if not bot_token or not chat_id or bot_token == "your_telegram_bot_token":
        print("Telegram configuration missing. Skipping notification.")
        return False
        
    base_url = f"https://api.telegram.org/bot{bot_token}"
    
    payload = {
        "chat_id": chat_id,
        "parse_mode": "HTML"
    }
    
    if inline_keyboard:
        payload["reply_markup"] = {"inline_keyboard": inline_keyboard}

    try:
        if photo_url:
            # Send as photo
            payload["photo"] = photo_url
            payload["caption"] = text
            requests.post(f"{base_url}/sendPhoto", json=payload)
        else:
            # Send as text
            payload["text"] = text
            requests.post(f"{base_url}/sendMessage", json=payload)
        return True
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False
