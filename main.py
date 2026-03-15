from flask import Flask, request, render_template, jsonify
import json
import os
import requests

app = Flask(__name__)
JSON_FILE = "data.json"
EXTERNAL_REMOVE_URL = "https://example-45gu.onrender.com/remove-request"

# Load JSON safely
def load_json():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
        except json.JSONDecodeError:
            data = []
    return data

# -----------------------------
# Show requests page
# -----------------------------
@app.get('/')
def index():
    data = load_json()
    headers = data[0].keys() if data and isinstance(data[0], dict) else []

    # Number of users is just the number of requests
    user_count = len(data)

    return render_template("requests.html", headers=headers, data=data, user_count=user_count)


# -----------------------------
# Remove a specific request
# -----------------------------
@app.post("/remove-request/<int:index>")
def remove_request(index):
    data = load_json()

    if index < 0 or index >= len(data):
        return jsonify({"success": False, "error": "Invalid index"})

    row = data[index]

    # Send to external server
    try:
        response = requests.post(EXTERNAL_REMOVE_URL, json=row)
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"External server returned {response.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to contact external server: {str(e)}"})

    # Remove row locally
    data.pop(index)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return jsonify({"success": True, "removed": row})


# -----------------------------
# Migrate requests / IPs
# -----------------------------
@app.post("/migrate-requests")
@app.post("/migrate-ip")
def migrate():
    data = request.json
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)