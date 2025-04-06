from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get("SESSION_SECRET", "changeme")

events_file = 'events.json'
users_file = 'users.json'

# Ensure files exist
for file in [events_file, users_file]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)

@app.route('/')
def index():
    return '✅ Backend is running'

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400

    with open(users_file, 'r+') as f:
        users = json.load(f)
        if any(u["username"] == username for u in users):
            return jsonify({"error": "Username already exists."}), 409

        users.append({"username": username, "password": password})
        f.seek(0)
        json.dump(users, f, indent=2)
    
    return jsonify({"message": "User registered."})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    with open(users_file, 'r') as f:
        users = json.load(f)
        for user in users:
            if user["username"] == username and user["password"] == password:
                session["user"] = username
                return jsonify({"message": "Login successful."})

    return jsonify({"error": "Invalid credentials."}), 401

@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out."})

@app.route("/me")
def get_user():
    if "user" in session:
        return jsonify({"logged_in": True, "username": session["user"]})
    return jsonify({"logged_in": False})

@app.route("/events", methods=["GET", "POST", "OPTIONS"])
def events():
    if request.method == 'OPTIONS':
        return '', 200
    elif request.method == 'POST':
        if "user" not in session:
            return jsonify({"error": "Unauthorized"}), 401

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
