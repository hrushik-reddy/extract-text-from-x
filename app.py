from flask import Flask, request, jsonify, render_template_string
import os
from werkzeug.utils import secure_filename
from text_extractors import extract_text_from_image, extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt, get_file_type
import gc
import threading

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'dev_key_not_secure'


processing_cache = {}
cache_lock = threading.Lock()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'txt', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cache_result(filename, text):
    """Cache processing results - BUG: Never clears cache, causing memory leak"""
    with cache_lock:

        processing_cache[filename] = {
            'text': text,
            'timestamp': os.path.getmtime(filename) if os.path.exists(filename) else 0,
            'size': os.path.getsize(filename) if os.path.exists(filename) else 0,
            'processed_data': text * 3  
        }

def get_cached_result(filename):
    """Check if result is cached"""
    with cache_lock:
        return processing_cache.get(filename, {}).get('text')

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Text Extractor</title>
    </head>
    <body>
        <h1>Extract Text from Files</h1>
        <form method="post" action="/extract" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Extract Text</button>
        </form>
        <p>Cache size: {cache_size} files</p>
    </body>
    </html>
    """.format(cache_size=len(processing_cache))
    return render_template_string(html_template)

@app.route('/extract', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'filename': '', 'extracted_text': '', 'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'filename': '', 'extracted_text': '', 'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Check cache first
        cached_text = get_cached_result(filename)
        if cached_text:
            return jsonify({
                'filename': filename,
                'extracted_text': cached_text,
                'error': None,
                'cached': True
            }), 200
        
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            file_extension = filename.rsplit('.', 1)[1].lower()
            extracted_text = ''
            
            if file_extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff']:
                extracted_text = extract_text_from_image(filepath)
            elif file_extension == 'pdf':
                extracted_text = extract_text_from_pdf(filepath)
            elif file_extension == 'docx':
                extracted_text = extract_text_from_docx(filepath)
            elif file_extension == 'txt':
                extracted_text = extract_text_from_txt(filepath)
            else:
                return jsonify({'filename': filename, 'extracted_text': '', 'error': 'Unsupported file type'}), 400
            
            # Cache the result (BUG: This will grow indefinitely)
            cache_result(filepath, extracted_text)
            
            return jsonify({
                'filename': filename,
                'extracted_text': extracted_text,
                'error': None,
                'cached': False
            }), 200
            
        except ValueError as ve:
            return jsonify({'filename': filename, 'extracted_text': '', 'error': str(ve)}), 500
        except Exception as e:
            return jsonify({'filename': filename, 'extracted_text': '', 'error': f'Error processing file: {str(e)}'}), 500
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
    
    else:
        return jsonify({'filename': file.filename if file else '', 'extracted_text': '', 'error': 'File type not allowed'}), 400

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'cache_size': len(processing_cache),
        'memory_usage': f"{len(str(processing_cache))} characters in cache"
    })

@app.route('/stats')
def stats():
    """New endpoint to show cache statistics"""
    return jsonify({
        'total_cached_files': len(processing_cache),
        'cache_keys': list(processing_cache.keys())[:10],  # Show first 10 keys
        'estimated_memory_usage': sum(len(str(v)) for v in processing_cache.values())
    })

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(host='0.0.0.0', port=5000, debug=True)