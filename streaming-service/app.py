from flask import Flask, Response, request, send_file, abort
from prometheus_flask_exporter import PrometheusMetrics
import os
import re
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# This path MUST match the volume mount in your docker-compose.yml
VIDEO_DIR = os.environ.get("UPLOADS_DIR", "/app/uploads_data/videos")

def generate_chunks(filepath, start, length):
    """Yields chunks of the video file."""
    try:
        with open(filepath, 'rb') as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk_size = 4096 if remaining > 4096 else remaining
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                remaining -= len(chunk)
    except Exception as e:
        logger.error(f"Error yielding video chunks: {e}")

@app.route('/stream/<filename>')
def stream_video(filename):
    video_path = os.path.join(VIDEO_DIR, filename)
    logger.info(f"Attempting to stream video from path: {video_path}")

    if not os.path.exists(video_path) or not os.path.isfile(video_path):
        logger.error(f"Video file not found at path: {video_path}")
        abort(404, description="Video not found")

    file_size = os.path.getsize(video_path)
    range_header = request.headers.get('Range', None)

    if not range_header:
        # If no Range header, send the whole file
        return send_file(video_path, mimetype='video/mp4', as_attachment=False)

    start_byte, end_byte = 0, None
    match = re.search(r'bytes=(\d+)-(\d*)', range_header)
    if not match:
        logger.error(f"Malformed Range header: {range_header}")
        return "Malformed Range header", 400
    
    groups = match.groups()
    start_byte = int(groups[0])
    if groups[1]:
        end_byte = int(groups[1])
    
    if end_byte is None or end_byte >= file_size:
        end_byte = file_size - 1

    length = end_byte - start_byte + 1

    resp = Response(
        generate_chunks(video_path, start_byte, length),
        206,  # 206 Partial Content
        mimetype='video/mp4',
        direct_passthrough=True
    )
    resp.headers.add('Content-Range', f'bytes {start_byte}-{end_byte}/{file_size}')
    resp.headers.add('Accept-Ranges', 'bytes')
    resp.headers.add('Content-Length', str(length))
    return resp

if __name__ == '__main__':
    logger.info("Starting Streaming Service...")
    app.run(host='0.0.0.0', port=5000, debug=True)