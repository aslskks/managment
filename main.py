from flask import Flask, request, render_template, jsonify, redirect, url_for
import json
import os
import requests

app = Flask(__name__)
JSON_FILE = "data.json"
EXTERNAL_REMOVE_URL = "https://example-45gu.onrender.com/remove-request"

# Load JSON safely
def load_json():
    if not os.path.exists(JSON_FILE):
        return {"requests": [], "ips": []}
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {"requests": [], "ips": []}
        except json.JSONDecodeError:
            data = {"requests": [], "ips": []}
    print(data)
    return data

# -----------------------------
# Show requests page
# -----------------------------
@app.route('/')
def index():
    all_data = load_json()
    requests_data = all_data.get("requests", [])
    ips_data = all_data.get("ips", [])
    user_count = len(ips_data)
    return render_template('requests.html', data=requests_data, user_count=user_count)

# -----------------------------
# Remove a specific request
# -----------------------------
@app.route("/remove-request/<int:index>", methods=["POST"])
def remove_request(index):
    all_data = load_json()
    requests_list = all_data.get("requests", [])

    if index < 0 or index >= len(requests_list):
        return jsonify({"success": False, "error": "Invalid index"})

    row = requests_list[index]

    # Send to external server
    try:
        response = requests.post(EXTERNAL_REMOVE_URL, json=row)
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"External server returned {response.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to contact external server: {str(e)}"})

    # Remove row locally
    requests_list.pop(index)
    all_data['requests'] = requests_list
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)

    # Redirect back to main page instead of returning JSON
    return redirect(url_for('index'))

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
        print("migrate success")
        return jsonify({"success": True})
    except Exception as e:
        print("migrate error: " + str(e))
        return jsonify({"success": False, "error": str(e)})

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)