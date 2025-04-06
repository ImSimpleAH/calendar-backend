from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
import os
import json
import requests

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get("SESSION_SECRET", "changeme")

# Discord OAuth2 config
CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI")  # e.g. https://your-backend.onrender.com/callback

API_BASE_URL = "https://discord.com/api"
OAUTH_AUTHORIZE_URL = f"{API_BASE_URL}/oauth2/authorize"
OAUTH_TOKEN_URL = f"{API_BASE_URL}/oauth2/token"
USER_API_URL = f"{API_BASE_URL}/users/@me"

SCOPES = "identify"

events_file = 'events.json'

# Ensure the events file exists
if not os.path.exists(events_file):
    with open(events_file, 'w') as f:
        json.dump([], f)

@app.route('/')
def index():
    return '✅ Backend is running'

@app.route('/login')
def login():
    return redirect(
        f"{OAUTH_AUTHORIZE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES}"
    )

@app.route('/callback')
def callback():
    code = request.args.get("code")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    token_res = requests.post(OAUTH_TOKEN_URL, data=data, headers=headers)
    token_res.raise_for_status()
    token_json = token_res.json()
    access_token = token_json.get("access_token")

    user_res = requests.get(USER_API_URL, headers={"Authorization": f"Bearer {access_token}"})
    user_res.raise_for_status()
    user_data = user_res.json()

    session["user"] = {
        "id": user_data["id"],
        "username": f"{user_data['username']}#{user_data['discriminator']}",
        "avatar": user_data.get("avatar")
    }
    return redirect("https://imsimpleah.github.io")  # Change if your frontend URL is different

@app.route("/me")
def get_user():
    user = session.get("user")
    if not user:
        return jsonify({"logged_in": False}), 401
    return jsonify({"logged_in": True, "user": user})

@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route("/events", methods=["GET", "POST", "OPTIONS"])
def events():
    if request.method == 'OPTIONS':
        return '', 200
    elif request.method == 'POST':
        try:
            data = request.json
            with open(events_file, 'r+') as f:
                try:
                    events = json.load(f)
                except json.JSONDecodeError:
                    events = []
                events.append(data)
                f.seek(0)
                json.dump(events, f, indent=2)
            return jsonify({"message": "Event added"}), 201
        except Exception as e:
            print("Error saving event:", e)
            return jsonify({"error": "Failed to save event."}), 500
    else:  # GET request
        try:
            with open(events_file, 'r') as f:
                events = json.load(f)
        except Exception:
            events = []
        return jsonify(events)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
