from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulação de base de dados em memória
streaming_sessions = []

@app.route('/')
def hello():
    return "Hello from Streaming Service"

@app.route('/stream', methods=['POST'])
def start_stream():
    data = request.get_json()
    if not data or 'video_id' not in data:
        return jsonify({'error': 'Missing video_id'}), 400
    
    session = {
        'session_id': len(streaming_sessions) + 1,
        'video_id': data['video_id']
    }
    streaming_sessions.append(session)
    return jsonify({'message': 'Streaming started', 'session': session}), 201

@app.route('/stream', methods=['GET'])
def list_streams():
    return jsonify(streaming_sessions), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)