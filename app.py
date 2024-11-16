from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
import shutil
from gradio_client import Client, handle_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def generate_and_save_image(prompt, image_path, save_filename="generated_image.webp"):
    client = Client("Kwai-Kolors/Kolors-FaceID")
    
    result = client.predict(
        prompt=prompt,
        image=handle_file(image_path),
        negative_prompt="",
        seed=0,
        randomize_seed=True,
        guidance_scale=5,
        num_inference_steps=25,
        api_name="/infer"
    )
    
    temp_image_path = result[0]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(current_dir, save_filename)
    
    shutil.copy2(temp_image_path, save_path)
    return save_path

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    prompt = request.form.get('prompt', '')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            generated_path = generate_and_save_image(prompt, filepath)
            return jsonify({
                'message': 'Image generated successfully',
                'filename': 'generated_image.webp'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/generated_image.webp')
def serve_generated_image():
    return send_from_directory('.', 'generated_image.webp')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))