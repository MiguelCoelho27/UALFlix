from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route("/admin/videos")
def test():
    try:
        r = requests.get("http://ualflix_catalog:5000/videos")
        return Response(r.content, status=r.status_code, content_type='application/json')
    except Exception as e:
        print("Erro ao contactar o catalog:", e)
        return Response(f'{{"error": "{str(e)}"}}', status=500, content_type='application/json')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
