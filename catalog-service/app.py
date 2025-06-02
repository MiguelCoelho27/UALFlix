from flask import Flask, request, jsonify
import db
from bson import ObjectId

app = Flask(__name__)

@app.route('/videos', methods=['POST'])
def create_video_route():
    data = request.get_json()
    
    if not data or not all(k in data for k in ("title", "description", "duration", "genre", "video_url")):
        return jsonify({"error": "Missing fields: title, description, duration, genre, video_url are required"}), 400
    
    video_id = db.create_video(
        data['title'], data['description'], 
    )
    
    if video_id:
        # Retornar a data do video
        create_video = db.get_video_by_id(video_id)
        return jsonify(create_video), 201
    else:
        return jsonify({"error": "Failed to create video"}), 500
    
@app.route('/videos/<video_id>', methods=['GET'])
def get_video_route(video_id):
    video = db.get_video_by_id(video_id)
    if video:
        return jsonify(video)
    else:
        return jsonify({"error": "Video not foud"}), 404
    
@app.route('/videos', methods=['PUT'])
def update_video_route(video_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data for update"}), 400
    
    success = db.update_video(video_id, data)
    if success:
        update_video = db.get_video_by_id(video_id)
        return jsonify({"status": "success", "video": update_video}), 200
    else:
        return jsonify({"error": "Video not found or update failed"}), 404
    
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
        return jsonify({"status": "success"}), 200
    else:
        return Jsonify({"error": "Video not found"}), 404
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    
