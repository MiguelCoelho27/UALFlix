from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename 
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)
UPLOADS_FOLDER = "uploads_data" # Mudança só para evitar problemas 
UPLOADS_METADATA_FILE = os.path.join(UPLOADS_FOLDER, "uploads.json")
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'} # Extensões de videos aceites para upload

app.config['UPLOAD_FOLDER'] = UPLOADS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 

# Garantir que a pasta existe
os.makedirs(UPLOADS_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOADS_FOLDER, "videos"), exist_ok=True) # Uma subfolder para os videos


# Inicializar ficheiro se não existir
if not os.path.exists(UPLOADS_METADATA_FILE):
    with open(UPLOADS_METADATA_FILE, 'w') as f:
        json.dump([], f)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_video_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    title = request.form.get('title')
    description = request.form.get('description')
    # genre = request.form.get('genre')
    
    if not title or not description:
        return jsonify({"error": "Missing title or description"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], "videos", filename)
        file.save(video_path)
        
        # Updating Metadata
        with open(UPLOADS_METADATA_FILE, 'r+') as f:
            uploads_metadata = json.load(f)
            video_id = len(uploads_metadata) + 1
            new_entry = {
                "id": video_id,
                "filename": filename,
                "filepath": video_path, # Storing aactual file path
                "title": title,
                # "genre": genre,
                "timestamp": datetime.now().isoformat(),
                "status": "uploaded"
            }
            
            uploads_metadata.append(new_entry)
            f.seek(0)
            f.truncate() # Clear file before wiring new data
            json.dump(uploads_metadata, f, indent=2)
        
        # TODO: Adicionar notificações no catalogo sobre novos videos ?
        return jsonify({"message": f"File '{filename}' uploaded successfully", "id": video_id, "title":title}), 201
    else:
        return jsonify({"error": "File type not allowed"}), 400


@app.route('/uploads', methods=['GET'])
def list_uploads_metadata():
    if not os.path.exists(UPLOADS_METADATA_FILE):
        return jsonify([])
    try:
        with open(UPLOADS_METADATA_FILE, 'r') as f:
            uploads_metadata = json.load(f)
        return jsonify(uploads_metadata), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Metadata file is corrupted"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)