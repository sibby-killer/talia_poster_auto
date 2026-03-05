import os
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv

# We will load supabase from the helper file
from supabase_client import get_supabase
from telegram_bot import send_telegram_notification
from scheduler import start_scheduler
from fb_poster import post_to_facebook

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# --- Decorators to protect routes ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Main Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # 1. Get form data
    handle = request.form.get('handle')
    gender = request.form.get('gender')
    intent = request.form.get('intent')
    whatsapp = request.form.get('whatsapp', '')
    description = request.form.get('description')
    photo = request.files.get('photo')

    supabase = get_supabase()

    # Fallback/Fail-safe if user submits without DB connected
    if not supabase:
        flash("System is currently under maintenance (Database disconnected). Please try again later.", "error")
        return redirect(url_for('index'))

    if not photo:
        flash("Please upload a photo.", "error")
        return redirect(url_for('index'))

    # 2. Upload photo to Supabase Storage (Assumes a bucket named 'submissions')
    try:
        filename = secure_filename(photo.filename)
        # Create a unique path
        unique_path = f"public/{os.urandom(8).hex()}_{filename}"
        
        photo_bytes = photo.read()
        res = supabase.storage.from_("submissions").upload(
            file=photo_bytes,
            path=unique_path,
            file_options={"content-type": photo.content_type}
        )
        
        # Get public URL
        image_url = supabase.storage.from_("submissions").get_public_url(unique_path)
    except Exception as e:
        print(f"Error uploading image: {e}")
        flash("Failed to upload image. Make sure the 'submissions' bucket exists and is public.", "error")
        return redirect(url_for('index'))

    # 3. Save to Supabase DB (table 'submissions')
    try:
        data = {
            "handle": handle,
            "gender": gender,
            "intent": intent,
            "whatsapp": whatsapp,
            "description": description,
            "image_url": image_url,
            "status": "Pending",
            "user_id": session.get('user', {}).get('id') # Attach to user if they are logged in while submitting
        }
        inserted_data = supabase.table("submissions").insert(data).execute()
        flash("Your profile was submitted successfully and is pending review!", "success")
        
        if inserted_data.data:
            sub_id = inserted_data.data[0]['id']
            domain = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5000")
            admin_message = f"<b>New Submission!</b>\nName: {handle}\nGender: {gender}\nIntent: {intent}\nWhatsApp: {whatsapp}\n\n<i>{description}</i>"
            keyboard = [
                [{"text": "✅ Approve & Post", "url": f"{domain}/admin/review/{sub_id}?action=approve"}],
                [{"text": "❌ Reject", "url": f"{domain}/admin/review/{sub_id}?action=reject"}]
            ]
            send_telegram_notification(admin_message, image_url, inline_keyboard=keyboard)
    except Exception as e:
        print(f"Error saving to db: {e}")
        flash("Error saving submission. Make sure the DB table exists.", "error")

    return redirect(url_for('index'))


# --- Auth Routes ---
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/auth/register', methods=['POST'])
def auth_register():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for('register'))

    supabase = get_supabase()
    if not supabase:
        flash("Database disconnected.", "error")
        return redirect(url_for('register'))

    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Registration failed.", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for('register'))

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/auth/login', methods=['POST'])
def auth_login():
    email = request.form.get('email')
    password = request.form.get('password')

    supabase = get_supabase()
    if not supabase:
        flash("Database disconnected.", "error")
        return redirect(url_for('login'))

    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            session['user'] = {'id': response.user.id, 'email': response.user.email}
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash("Invalid email or password.", "error")

    return redirect(url_for('login'))

@app.route('/auth/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# --- Dashboard Routes ---
@app.route('/dashboard')
@login_required
def dashboard():
    supabase = get_supabase()
    user_id = session['user']['id']
    
    try:
        # Fetch submissions for this user
        response = supabase.table("submissions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        submissions = response.data
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        submissions = []

    return render_template('dashboard.html', user=session['user'], submissions=submissions)

@app.route('/dashboard/delete/<int:sub_id>', methods=['POST'])
@login_required
def delete_submission(sub_id):
    supabase = get_supabase()
    user_id = session['user']['id']
    try:
        # Ensure the user requesting deletion owns the submission
        supabase.table("submissions").delete().match({"id": sub_id, "user_id": user_id}).execute()
        flash("Submission deleted successfully.", "success")
    except Exception as e:
        flash("Error deleting submission.", "error")
        
    return redirect(url_for('dashboard'))

# --- Admin Routes ---
@app.route('/admin/review/<int:sub_id>')
def admin_review(sub_id):
    action = request.args.get('action')
    supabase = get_supabase()
    
    try:
        sub = supabase.table("submissions").select("*").eq("id", sub_id).execute()
        if not sub.data:
            return "Submission not found.", 404
            
        submission = sub.data[0]
        
        if action == 'approve':
            fb_msg = f"{submission['handle']} is looking for a {submission['intent']}! 🌟\n\nBio: {submission['description']}\nWhatsApp: {submission['whatsapp']}"
            link_comment = "Want to be featured? Submit your profile here to join the community! 👉 [YOUR_WEBSITE_LINK]"
            
            fb_link = post_to_facebook(submission['image_url'], fb_msg, link_comment)
            
            supabase.table("submissions").update({
                "status": "Approved",
                "fb_link": fb_link or ""
            }).eq("id", sub_id).execute()
            
            return f"<h1>Approved!</h1><p>Successfully posted to Facebook.</p><a href='{fb_link}'>View Post</a>"
            
        elif action == 'reject':
            supabase.table("submissions").update({"status": "Rejected"}).eq("id", sub_id).execute()
            return "<h1>Rejected</h1><p>The submission was marked as rejected.</p>"
        
        return "Invalid action."
    except Exception as e:
        return f"Error processing review: {e}"

if __name__ == '__main__':
    start_scheduler()
    app.run(debug=True, port=5000)
