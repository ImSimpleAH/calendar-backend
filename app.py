from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

events_file = 'events.json'

# Make sure events.json exists
if not os.path.exists(events_file):
    with open(events_file, 'w') as f:
        json.dump([], f)

@app.route('/')
def home():
    return '✅ 28th CAD Calendar API is running!'

@app.route('/events', methods=['GET'])
def get_events():
    try:
        with open(events_file, 'r') as f:
            events = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        events = []
    return jsonify(events)

@app.route('/events', methods=['POST', 'OPTIONS'])
def add_event():
    if request.method == 'OPTIONS':
        # Preflight request — just return a 200
        return '', 200

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

# Bind to 0.0.0.0 and port from Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
