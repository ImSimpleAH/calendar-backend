from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

events_file = 'events.json'

# Ensure the events file exists
if not os.path.exists(events_file):
    with open(events_file, 'w') as f:
        json.dump([], f)

@app.route('/events', methods=['GET', 'POST', 'OPTIONS'])
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

