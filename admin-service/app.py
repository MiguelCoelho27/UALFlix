from flask import Flask, Response, request
import requests

app = Flask(__name__)
CATALOG_SERVICE_URL = "http://catalog:5000/videos"

@app.route("/videos", methods=['GET', 'POST'])
def handle_videos_collection():
    """Handle listing all videos and adding a new one."""
    if request.method == 'POST':
        try:
            video_data = request.get_json()
            if not video_data:
                return Response('{"error": "Invalid JSON"}', status=400, content_type='application/json')
            # Forward the POST request to the catalog-service
            r = requests.post(CATALOG_SERVICE_URL, json=video_data)
            return Response(r.content, status=r.status_code, content_type=r.headers['content-type'])
        except Exception as e:
            return Response(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')
    
    # Handle GET request (listing)
    try:
        r = requests.get(CATALOG_SERVICE_URL)
        return Response(r.content, status=r.status_code, content_type='application/json')
    except Exception as e:
        return Response(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')

@app.route("/videos/<video_id>", methods=['PUT', 'DELETE'])
def handle_specific_video(video_id):
    """Handle updating or deleting a specific video."""
    video_specific_url = f"{CATALOG_SERVICE_URL}/{video_id}"

    if request.method == 'PUT':
        try:
            video_data = request.get_json()
            if not video_data:
                return Response('{"error": "Invalid JSON"}', status=400, content_type='application/json')
            # Forward the PUT request to the catalog-service
            r = requests.put(video_specific_url, json=video_data)
            return Response(r.content, status=r.status_code, content_type=r.headers['content-type'])
        except Exception as e:
            return Response(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')

    if request.method == 'DELETE':
        try:
            # Forward the DELETE request to the catalog-service
            r = requests.delete(video_specific_url)
            return Response(r.content, status=r.status_code, content_type=r.headers['content-type'])
        except Exception as e:
            return Response(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)