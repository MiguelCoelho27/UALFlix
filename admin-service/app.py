from flask import Flask, Response, request
import requests

app = Flask(__name__)
CATALOG_SERVICE_URL = "http://catalog:5000/videos"

@app.route("/admin/videos", methods=['GET', 'POST'])
def handle_videos():
    # Handling POST Request to add new videos here
    if request.method == 'POST':
        try:
            # JSON data from the request
            video_data = request.get_json()
            if not video_data:
                return Response('{"error": "Invalid JSON"}', status=400, content_type='application/json')
            
            # Forward POST Request to Catalog
            r = requests.post(CATALOG_SERVICE_URL, json=video_data)
            
            # Response from the catalog-service
            return Response(r.content, status=r.status_code, content_type=r.headers['content-type'])
        except Exception as e:
            return Response(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')
    # GET to list all videos
    if request.method == "GET":
        try:
            r = requests.get(CATALOG_SERVICE_URL)
            return Response(r.content, status=r.status_code, content_type='application/json')
        except Exception as e:
            return Response(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
