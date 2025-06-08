from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename 
import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import requests 
import logging # adicionado para perceber uns problemas 

app = Flask(__name__)
CORS(app)

# logs basics
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOADS_FOLDER_BASE = os.environ.get("UPLOADS_DIR", "/app/uploads_data") 
VIDEO_FILES_SUBDIR = "videos" 
VIDEO_FILES_PATH = os.path.join(UPLOADS_FOLDER_BASE, VIDEO_FILES_SUBDIR)

app.config['UPLOAD_FOLDER'] = VIDEO_FILES_PATH
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://ualflix_admin:ualflix_password@mongodb-service:27017/ualflix?replicaSet=ualflix-rs&authSource=admin")
client = MongoClient(MONGO_URI)
db = client.get_database()
uploads_metadata_collection = db["uploads_metadata"]

os.makedirs(UPLOADS_FOLDER_BASE, exist_ok=True)
os.makedirs(VIDEO_FILES_PATH, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_video_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    title = request.form.get('title')
    description = request.form.get('description')
    genre = request.form.get('genre', 'General')
    
    if not title or not description:
        return jsonify({"error": "Missing title or description"}), 400
    
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        unique_id_for_file = str(ObjectId()) 
        _, ext = os.path.splitext(original_filename)
        stored_filename = f"{unique_id_for_file}{ext}"
        
        video_path_in_volume = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)
        
        try:
            file.save(video_path_in_volume)
        except Exception as e:
            logger.error(f"Failed to save file '{stored_filename}': {e}")
            return jsonify({"error": f"Server error: Could not save file. {str(e)}"}), 500

        
        video_access_url = f"/static_videos/{stored_filename}" 

        upload_metadata_entry = {
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "filepath_in_volume": video_path_in_volume,
            "video_access_url": video_access_url,
            "title": title,
            "description": description,
            "genre": genre,
            "timestamp": datetime.now().isoformat(),
            "status": "uploaded",
            "content_type": file.content_type,
            "size_bytes": file.content_length 
        }
        
        try:
            result = uploads_metadata_collection.insert_one(upload_metadata_entry)
            inserted_id_str = str(result.inserted_id)
            
            # Notificar o catalog-service
            catalog_service_url = os.environ.get("CATALOG_SERVICE_URL", "http://catalog-service:5000/videos")
            duration_seconds = 0 
            
            catalog_payload = {
                "title": title,
                "description": description,
                "duration": duration_seconds, 
                "genre": genre,
                "video_url": video_access_url 
            }
            logger.info(f"Attempting to notify catalog service at {catalog_service_url} with payload: {catalog_payload}")
            
            try:
                response = requests.post(catalog_service_url, json=catalog_payload, timeout=10) # Increased timeout
                response.raise_for_status() # Raises an exception for HTTP errors (4xx or 5xx)
                logger.info(f"Successfully notified catalog service for video: {title}. Response: {response.json()}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to notify catalog service for video '{title}': {e}")
                pass 

            return jsonify({
                "message": f"File '{original_filename}' uploaded successfully as '{stored_filename}'. Catalog notification attempted.", 
                "upload_id": inserted_id_str,
                "title": title,
                "video_access_url": video_access_url
            }), 201
        except Exception as e:
            logger.error(f"Failed to insert metadata to MongoDB for '{original_filename}': {e}")
            try:
                os.remove(video_path_in_volume)
                logger.info(f"Cleaned up orphaned file: {video_path_in_volume}")
            except OSError as oe:
                logger.error(f"Error cleaning up orphaned file '{video_path_in_volume}': {oe}")
            return jsonify({"error": f"Server error: Could not save video metadata. {str(e)}"}), 500
    else:
        return jsonify({"error": "File type not allowed or no file provided."}), 400

@app.route('/uploads', methods=['GET'])
def list_uploads_metadata():
    try:
        all_uploads = []
        for upload_doc in uploads_metadata_collection.find():
            upload_doc["_id"] = str(upload_doc["_id"])
            all_uploads.append(upload_doc)
        return jsonify(all_uploads), 200
    except Exception as e:
        logger.error(f"Failed to retrieve uploads metadata from MongoDB: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
