from flask import Flask, Response, request
import requests

app = Flask(__name__)
CATALOG_SERVICE_URL = "http://catalog:5000/videos"

@app.route("/videos", methods=['GET'])
def get_all_videos_route():
    try:
        r = requests.get(CATALOG_SERVICE_URL)
        return Response(r.content, status=r.status_code, content_type='application/json')
    except Exception as e:
        return Response(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')

@app.route("/videos/<video_id>", methods=['PUT', 'DELETE'])
def manage_specific_video_route(video_id):
    video_specific_url = f"{CATALOG_SERVICE_URL}/{video_id}"

    if request.method == 'PUT':
        try:
            video_data = request.get_json()
            if not video_data:
                return Response('{"error": "Invalid JSON"}', status=400, content_type='application/json')
            
            r = requests.put(video_specific_url, json=video_data)
            return Response(r.content, status=r.status_code, content_type=r.headers['content-type'])
        
        except Exception as e:
            return Response(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')

    if request.method == 'DELETE':
        try:
            r = requests.delete(video_specific_url)
            return Response(r.content, status=r.status_code, content_type=r.headers['content-type'])
        
        except Exception as e:
            return Response(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)