from flask import Flask, request, render_template,jsonify
import json
import os
import requests
app = Flask(__name__)
JSON_FILE = "data.json"
EXTERNAL_REMOVE_URL = "https://games-8upn.onrender.com/remove-request"
@app.post("/migrate-requests")
def migrate():
    data = request.json
    try:
        with open(JSON_FILE, "w") as file:
            json.dump(data, file, indent=4)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
@app.get('/')
def index():
    if not os.path.exists(JSON_FILE):
        return "No requests yet."

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    headers = data[0].keys() if data else []
    return render_template("requests.html", headers=headers, data=data)
@app.route("/remove-request/<int:index>", methods=["POST"])
def remove_request(index):
    if not os.path.exists(JSON_FILE):
        return jsonify({"success": False, "error": "File not found"})

    try:
        # Load local data
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if index < 0 or index >= len(data):
            return jsonify({"success": False, "error": "Invalid index"})

        row = data[index]  # the row we want to remove

        # Send row data to external page to remove it there
        response = requests.post(EXTERNAL_REMOVE_URL, json=row)
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"External server returned {response.status_code}"})

        # Remove row locally
        data.pop(index)
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        return jsonify({"success": True, "removed": row})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
app.run(debug=True, port=10000, host="0.0.0.0")