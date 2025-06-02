from flask import Flask, request, jsonify
from flask_cors import CORS
import db 

app = Flask(__name__)
CORS(app) 

@app.route('/videos', methods=['POST'])
def create_video_route():
    data = request.get_json()
    
    required_fields = ["title", "description", "duration", "genre", "video_url"]
    if not data or not all(k in data for k in required_fields):
        missing = [k for k in required_fields if k not in data]
        return jsonify({"error": f"Missing fields: {', '.join(missing)} are required"}), 400

    if not isinstance(data.get('duration'), (int, float)):
        return jsonify({"error": "Field 'duration' must be a number (e.g., seconds)"}), 400

    video_id = db.create_video(
        data['title'], 
        data['description'], 
        data['duration'], 
        data['genre'], 
        data['video_url']
    )
    
    if video_id:
        created_video = db.get_video_by_id(video_id) 
        if created_video:
            return jsonify(created_video), 201
        else:
            return jsonify({"error": "Video created but could not be retrieved"}), 500
    else:
        return jsonify({"error": "Failed to create video in database"}), 500


@app.route('/videos/<video_id>', methods=['GET'])
def get_video_route(video_id):
    video = db.get_video_by_id(video_id)
    if video:
        return jsonify(video)
    else:
        return jsonify({"error": "Video not found"}), 404

@app.route('/videos', methods=['GET'])
def get_videos_route():
    videos = db.get_all_videos()
    return jsonify(videos)


@app.route('/videos/<video_id>', methods=['PUT'])
def update_video_route(video_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data for update"}), 400
    
    success = db.update_video(video_id, data)
    if success:
        updated_video = db.get_video_by_id(video_id)
        if updated_video:
            return jsonify({"status": "success", "video": updated_video}), 200
        else:
            return jsonify({"error": "Video updated but could not be retrieved"}), 404
    else:
        existing_video = db.get_video_by_id(video_id)
        if not existing_video:
            return jsonify({"error": "Video not found, cannot update"}), 404
        return jsonify({"error": "Update operation did not modify the video"}), 400


@app.route('/videos/<video_id>', methods=['DELETE'])
def delete_video_route(video_id):
    success = db.delete_video(video_id)
    if success:
        return jsonify({"status": "success", "message": "Video deleted"}), 200
    else:
        return jsonify({"error": "Video not found or delete failed"}), 404


@app.route('/videos/<video_id>/view', methods=['POST'])
def increment_view_route(video_id):
    success = db.increment_view_count(video_id)
    if success:
        return jsonify({"status": "success", "message": "View count incremented"}), 200
    else:
        return jsonify({"error": "Video not found or failed to increment view count"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
