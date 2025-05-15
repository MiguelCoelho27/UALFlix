from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulação de base de dados em memória
videos_db = []

@app.route('/videos', methods=['POST'])
def create_video():
    data = request.get_json()
    if not data or not all(k in data for k in ("title", "description", "duration")):
        return jsonify({"error": "Missing fields"}), 400
    
    new_video = {
        "id": len(videos_db) + 1,
        "title": data["title"],
        "description": data["description"],
        "duration": data["duration"]
    }
    videos_db.append(new_video)
    return jsonify(new_video), 201

@app.route('/videos', methods=['GET'])
def get_videos():
    return jsonify(videos_db), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
