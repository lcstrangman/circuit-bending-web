# app.py
import os
import io
from flask import Flask, request, send_file
import rawpy
from PIL import Image

app = Flask(__name__, static_folder='static', static_url_path='')
os.makedirs('temp', exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file", 400
    file = request.files['file']

    filename = file.filename.lower()
    
    try:
        if filename.endswith(('.dng', '.cr2', '.nef', '.arw')):
            # rawpy extracts the high-quality sensor data natively
            with rawpy.imread(file.stream) as raw:
                # Develop into an 8-bit RGB numpy array
                rgb_data = raw.postprocess(use_camera_wb=True)
                img = Image.fromarray(rgb_data)
        else:
            img = Image.open(file.stream).convert('RGB')

        # Send it back to the browser as a clean, high-res PNG
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        print(f"Error: {e}")
        return "Failed to process image", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)