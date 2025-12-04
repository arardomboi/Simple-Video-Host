from flask import Flask, request, Response, render_template, send_from_directory, abort
import os
import mimetypes

app = Flask(__name__, template_folder='templates')

# Directory to drop your videos into.
BASE_DIR = os.path.dirname(__file__)
VIDEO_DIR = os.path.join(BASE_DIR, 'videos')
os.makedirs(VIDEO_DIR, exist_ok=True)


def parse_range(range_header, file_size):
	# Parse a Range header like: 'bytes=0-1023'
	if not range_header:
		return None
	units, _, range_spec = range_header.partition('=')
	if units != 'bytes':
		return None
	start_str, _, end_str = range_spec.partition('-')
	try:
		start = int(start_str) if start_str else 0
	except ValueError:
		return None
	try:
		end = int(end_str) if end_str else file_size - 1
	except ValueError:
		end = file_size - 1
	if start > end or end >= file_size:
		return None
	return start, end


@app.route('/')
def index():
	# List available video files in the `videos/` directory
	try:
		files = [f for f in os.listdir(VIDEO_DIR) if os.path.isfile(os.path.join(VIDEO_DIR, f))]
	except Exception:
		files = []
	return render_template('index.html', videos=files)


@app.route('/video/<path:filename>')
def video(filename):
	# Prevent path traversal
	safe_path = os.path.normpath(os.path.join(VIDEO_DIR, filename))
	if not safe_path.startswith(os.path.abspath(VIDEO_DIR)):
		abort(404)
	if not os.path.exists(safe_path):
		abort(404)

	file_size = os.path.getsize(safe_path)
	range_header = request.headers.get('Range', None)
	if range_header:
		rng = parse_range(range_header, file_size)
		if rng is None:
			return Response(status=416)
		start, end = rng
		length = end - start + 1

		def generate():
			with open(safe_path, 'rb') as f:
				f.seek(start)
				remaining = length
				chunk_size = 8192
				while remaining > 0:
					read_size = min(chunk_size, remaining)
					data = f.read(read_size)
					if not data:
						break
					remaining -= len(data)
					yield data

		content_type = mimetypes.guess_type(safe_path)[0] or 'application/octet-stream'
		rv = Response(generate(), status=206, mimetype=content_type)
		rv.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
		rv.headers.add('Accept-Ranges', 'bytes')
		rv.headers.add('Content-Length', str(length))
		return rv
	else:
		# No range header; let Flask send the full file
		return send_from_directory(VIDEO_DIR, filename, as_attachment=False)


if __name__ == '__main__':
	# Run development server; access at http://localhost:5000/
	app.run(host='0.0.0.0', port=5000, debug=True)
