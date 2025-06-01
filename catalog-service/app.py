from flask import Flask, request, jsonify
import db

app = Flask(__name__)

@app.before_request
def setup():
    db.init_db()

@app.route('/videos', methods=['POST'])

def create_video():
    data = request.get_json()
    
    if not data or not all(k in data for k in ("title", "description", "duration")):
        return jsonify({"error": "Missing fields"}), 400

    video_id = db.create_video(data['title'], data['description'], data['duration'], data['genre'])
    
    
    return jsonify({
        "id": video_id,
        "title": data['title'],
        "description": data['description'],
        "duration": data['duration'],
        "genre": data['genre'],
    }), 201


@app.route('/videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    video = db.get_video_by_id(video_id)
    if video:
        return jsonify(video)
    else:
        return jsonify({"error": "Video not found"}), 404

@app.route('/videos', methods=['GET'])
def get_videos():
    videos = db.get_all_videos()
    return jsonify(videos)


@app.route('/videos/<int:video_id>/view', methods=['POST'])
def increment_view(video_id):
    success = db.increment_view_count(video_id)
    if success:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": "Video not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)