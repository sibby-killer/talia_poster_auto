import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=payload)


def send_photo(chat_id, photo_url, caption="", reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/sendPhoto", json=payload)


def send_telegram_notification(text, photo_url=None, inline_keyboard=None):
    """Called when a new user submission arrives."""
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        print("Telegram config missing. Skipping.")
        return False
    markup = {"inline_keyboard": inline_keyboard} if inline_keyboard else None
    if photo_url:
        send_photo(ADMIN_CHAT_ID, photo_url, text, markup)
    else:
        send_message(ADMIN_CHAT_ID, text, markup)
    return True


# ---- Persistent keyboard shown at the bottom of the chat ----
MAIN_KEYBOARD = {
    "keyboard": [
        [{"text": "📋 Main Menu"}, {"text": "📩 Pending Submissions"}],
        [{"text": "✅ Approved Posts"}, {"text": "🤖 Generate & Post Now"}],
        [{"text": "📊 Stats"}, {"text": "ℹ️ Help"}],
    ],
    "resize_keyboard": True,
    "persistent": True,          # Keeps keyboard visible always
}

WELCOME_TEXT = """
👋 <b>Welcome to the Talia Community Admin Bot!</b>

I help you manage the <b>Talia Rose Facebook page</b> community.

Here's what I do:
━━━━━━━━━━━━━━━━━━
📸 <b>User Submissions</b> — When someone submits a profile, I'll send it to you here with <b>Approve / Reject</b> buttons.

🤖 <b>AI Auto-Poster</b> — I generate & post beautiful SFW photos to Facebook <b>6x/day</b> at peak US engagement times.

📊 <b>Stats</b> — Check how many posts are live, pending, or rejected.

━━━━━━━━━━━━━━━━━━
<b>Available Commands:</b>
/start — Show this welcome message
/menu — Open the main menu
/pending — View pending submissions
/approved — View approved posts
/post — Generate & post an AI image now
/stats — View submission statistics
/help — Show all commands

<i>Use the quick buttons below ⬇️ to navigate!</i>
"""

MENU_TEXT = """
🎛️ <b>Main Menu</b>
━━━━━━━━━━━━━━━━━━
Choose an option below or use a quick button:

📩 <b>Pending</b> — Review user submissions waiting for approval
✅ <b>Approved</b> — See all approved & posted content
🤖 <b>Generate & Post</b> — Trigger an AI post immediately
📊 <b>Stats</b> — Content overview and counts
ℹ️ <b>Help</b> — All commands and guide
"""


def handle_update(update: dict):
    """
    Called from the Telegram webhook route in app.py.
    Handles all incoming messages and commands.
    """
    message = update.get("message", {})
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    # --- Commands ---
    if text in ["/start", "/start@" + get_bot_username()]:
        send_message(chat_id, WELCOME_TEXT, MAIN_KEYBOARD)

    elif text in ["/menu", "📋 Main Menu"]:
        send_message(chat_id, MENU_TEXT, MAIN_KEYBOARD)

    elif text in ["/pending", "📩 Pending Submissions"]:
        _handle_pending(chat_id)

    elif text in ["/approved", "✅ Approved Posts"]:
        _handle_approved(chat_id)

    elif text in ["/post", "🤖 Generate & Post Now"]:
        _handle_generate_post(chat_id)

    elif text in ["/stats", "📊 Stats"]:
        _handle_stats(chat_id)

    elif text in ["/help", "ℹ️ Help"]:
        send_message(chat_id, WELCOME_TEXT, MAIN_KEYBOARD)

    else:
        send_message(
            chat_id,
            "I didn't understand that. Use the buttons below or type /help",
            MAIN_KEYBOARD
        )


def get_bot_username():
    try:
        r = requests.get(f"{BASE_URL}/getMe").json()
        return r["result"]["username"]
    except:
        return ""


def _handle_pending(chat_id):
    from supabase_client import get_supabase
    supabase = get_supabase()
    if not supabase:
        send_message(chat_id, "❌ Database not connected.", MAIN_KEYBOARD)
        return
    try:
        res = supabase.table("submissions").select("*").eq("status", "Pending").order("created_at", desc=True).execute()
        subs = res.data
        if not subs:
            send_message(chat_id, "✅ No pending submissions right now!", MAIN_KEYBOARD)
            return
        send_message(chat_id, f"📩 <b>{len(subs)} Pending Submission(s):</b>", MAIN_KEYBOARD)
        for sub in subs[:5]:  # Show max 5 at a time
            text = (
                f"<b>#{sub['id']} — {sub['handle']}</b>\n"
                f"Gender: {sub['gender']} | Intent: {sub['intent']}\n"
                f"WhatsApp: {sub.get('whatsapp', 'N/A')}\n"
                f"Bio: {sub.get('description', '')[:100]}"
            )
            domain = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5000")
            keyboard = {"inline_keyboard": [
                [{"text": "✅ Approve & Post", "url": f"{domain}/admin/review/{sub['id']}?action=approve"}],
                [{"text": "❌ Reject", "url": f"{domain}/admin/review/{sub['id']}?action=reject"}],
            ]}
            if sub.get("image_url"):
                send_photo(chat_id, sub["image_url"], text, keyboard)
            else:
                send_message(chat_id, text, keyboard)
    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}", MAIN_KEYBOARD)


def _handle_approved(chat_id):
    from supabase_client import get_supabase
    supabase = get_supabase()
    if not supabase:
        send_message(chat_id, "❌ Database not connected.", MAIN_KEYBOARD)
        return
    try:
        res = supabase.table("submissions").select("*").eq("status", "Approved").order("created_at", desc=True).execute()
        subs = res.data
        if not subs:
            send_message(chat_id, "No approved posts yet.", MAIN_KEYBOARD)
            return
        lines = [f"• <b>{s['handle']}</b> — <a href='{s.get('fb_link', '#')}'>View Post</a>" for s in subs[:10]]
        send_message(chat_id, f"✅ <b>{len(subs)} Approved Post(s):</b>\n\n" + "\n".join(lines), MAIN_KEYBOARD)
    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}", MAIN_KEYBOARD)


def _handle_generate_post(chat_id):
    send_message(chat_id, "🤖 Generating an AI image and posting to Facebook... Give me 30 seconds! ⏳", MAIN_KEYBOARD)
    try:
        from scheduler import run_ai_job
        import threading
        threading.Thread(target=run_ai_job).start()
        send_message(chat_id, "✅ Job started! I'll post to Facebook in the background.", MAIN_KEYBOARD)
    except Exception as e:
        send_message(chat_id, f"❌ Failed to start job: {e}", MAIN_KEYBOARD)


def _handle_stats(chat_id):
    from supabase_client import get_supabase
    supabase = get_supabase()
    if not supabase:
        send_message(chat_id, "❌ Database not connected.", MAIN_KEYBOARD)
        return
    try:
        all_res = supabase.table("submissions").select("status").execute()
        all_subs = all_res.data
        pending = sum(1 for s in all_subs if s["status"] == "Pending")
        approved = sum(1 for s in all_subs if s["status"] == "Approved")
        rejected = sum(1 for s in all_subs if s["status"] == "Rejected")
        text = (
            f"📊 <b>Talia Community Stats</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Total Submissions: <b>{len(all_subs)}</b>\n"
            f"📩 Pending: <b>{pending}</b>\n"
            f"✅ Approved: <b>{approved}</b>\n"
            f"❌ Rejected: <b>{rejected}</b>"
        )
        send_message(chat_id, text, MAIN_KEYBOARD)
    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}", MAIN_KEYBOARD)
