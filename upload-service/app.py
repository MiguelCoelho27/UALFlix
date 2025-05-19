# upload-service/app.py
from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
UPLOADS_FOLDER = "uploads"
UPLOADS_FILE = os.path.join(UPLOADS_FOLDER, "uploads.json")

# Garantir que a pasta existe
os.makedirs(UPLOADS_FOLDER, exist_ok=True)

# Inicializar ficheiro se não existir
if not os.path.exists(UPLOADS_FILE):
    with open(UPLOADS_FILE, 'w') as f:
        json.dump([], f)

@app.route('/upload', methods=['POST'])
def upload_video():
    data = request.get_json()
    if not data or "filename" not in data:
        return jsonify({"error": "Missing filename"}), 400

    with open(UPLOADS_FILE, 'r+') as f:
        uploads = json.load(f)
        new_entry = {
            "id": len(uploads) + 1,
            "filename": data["filename"],
            "timestamp": datetime.now().isoformat()
        }
        uploads.append(new_entry)
        f.seek(0)
        json.dump(uploads, f, indent=2)

    return jsonify({"message": f"File '{data['filename']}' uploaded successfully", "id": new_entry["id"]}), 201

@app.route('/upload', methods=['GET'])
def list_uploads():
    with open(UPLOADS_FILE, 'r') as f:
        uploads = json.load(f)
    return jsonify(uploads), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)