from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Upload Service"

@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.get_json()
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "Filename is required"}), 400
    return jsonify({"message": f"File '{filename}' uploaded successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
