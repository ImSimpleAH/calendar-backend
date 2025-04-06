from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os

app = Flask(__name__)
CORS(app)

events_file = 'events.json'
if not os.path.exists(events_file):
    with open(events_file, 'w') as f:
        json.dump([], f)

@app.route('/events', methods=['GET'])
def get_events():
    try:
        with open(events_file, 'r') as f:
            events = json.load(f)
    except Exception as e:
        print("Error reading events.json:", e)
        events = []
    return jsonify(events)

@app.route('/events', methods=['POST'])
def add_event():
    data = request.json
    with open(events_file, 'r+') as f:
        events = json.load(f)
        events.append(data)
        f.seek(0)
        json.dump(events, f, indent=2)
    return jsonify({"message": "Event added"}), 201

@app.route('/')
def home():
    return '✅ 28th CAD Calendar API is running!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
