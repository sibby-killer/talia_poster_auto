# 🌟 Talia Community — AI-Powered Social Page

Live site: **https://talia-poster-auto.onrender.com**

A community matchmaking and content platform where real people can submit their profiles to be featured, and AI auto-generates beautiful content 6x/day to grow the page audience — targeting the US market.

---

## ✨ Features

- **User Profile Submissions** — People submit a photo, handle, gender, intent (friendship/partner), WhatsApp, and bio
- **AI Auto-Poster** — Generates hyper-realistic SFW full-body images with Hugging Face (`FLUX.1-schnell`) 6x/day, Pollinations.ai as fallback
- **Admin Review via Telegram** — Every submission triggers a Telegram message with ✅ Approve / ❌ Reject buttons
- **One-Click Facebook Posting** — Approved posts go directly to the Facebook page with caption + community link as first comment
- **User Dashboard** — Users can sign up, track submission status (Pending/Approved/Rejected), and delete/update their submissions
- **US EST Scheduling** — Posts at peak US engagement times: 8AM, 12PM, 3PM, 6PM, 8PM, 10PM EST
- **GitHub Actions Cron** — Scheduler runs entirely free via GitHub Actions (no server needed for posts)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Database & Auth | Supabase (PostgreSQL + Auth + Storage) |
| AI Image Generation | Hugging Face FLUX.1-schnell (primary), Pollinations.ai (fallback) |
| Scheduling | GitHub Actions (cron) |
| Hosting | Render (free tier) |
| Facebook Posting | Facebook Graph API |
| Admin Notifications | Telegram Bot API |

---

## 🚀 Setup

### 1. Clone the repo
```bash
git clone https://github.com/sibby-killer/talia_poster_auto.git
cd talia_poster_auto
pip install -r requirements.txt
```

### 2. Create `.env` file
Copy `.env.example` and fill in all values:
```bash
cp .env.example .env
```

Required keys:
- `SUPABASE_URL` and `SUPABASE_KEY` — from supabase.com
- `HF_API_TOKEN` — from huggingface.co/settings/tokens
- `FB_PAGE_ACCESS_TOKEN` and `FB_PAGE_ID` — from Facebook Graph API Explorer
- `TELEGRAM_BOT_TOKEN` and `ADMIN_CHAT_ID` — from @BotFather
- `RENDER_EXTERNAL_URL` — your live Render URL

### 3. Set up Supabase
Run this SQL in your Supabase SQL Editor:
```sql
CREATE TABLE submissions (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    handle TEXT, gender TEXT, intent TEXT,
    whatsapp TEXT, description TEXT,
    image_url TEXT, status TEXT DEFAULT 'Pending',
    fb_link TEXT, user_id UUID
);
```
Create a **public** storage bucket named `submissions`.

### 4. Run locally
```bash
python app.py
```

### 5. Deploy to Render
- Connect GitHub repo on render.com
- Start command: `gunicorn app:app`
- Add all `.env` values as environment variables

### 6. Set GitHub Secrets
Go to **Settings → Secrets → Actions** and add all keys from `.env` so the GitHub Actions cron job can post automatically.

---

## 📅 Posting Schedule (US EST)

| Time (EST) | Description |
|---|---|
| 8:00 AM | Morning scroll |
| 12:00 PM | Lunch break |
| 3:00 PM | Afternoon |
| 6:00 PM | Evening peak |
| 8:00 PM | Prime time |
| 10:00 PM | Night owls |

---

## 📁 Project Structure

```
├── app.py               # Main Flask application
├── ai_generator.py      # AI image generation (HuggingFace + Pollinations)
├── scheduler.py         # Scheduler logic with US hashtags + captions
├── run_post_job.py      # Standalone script called by GitHub Actions
├── fb_poster.py         # Facebook Graph API integration
├── telegram_bot.py      # Telegram admin notifications
├── supabase_client.py   # Supabase client helper
├── templates/           # HTML pages (index, login, register, dashboard)
├── static/css/          # Glassmorphism CSS styles
├── .github/workflows/   # GitHub Actions cron workflow
└── requirements.txt
```

---

> Built with ❤️ for the Talia Rose community page 🌹
