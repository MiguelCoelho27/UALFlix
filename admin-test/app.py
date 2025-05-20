from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route("/admin/videos")
def get_videos():
    try:
        response = requests.get("http://host.docker.internal:5001/videos")
        return Response(response.content, status=response.status_code, content_type="application/json")
    except Exception as e:
        return Response(f'{{"error": "{str(e)}"}}', status=500, content_type="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)