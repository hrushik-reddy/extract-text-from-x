
from flask import Flask, request, jsonify, render_template_string
import os
from werkzeug.utils import secure_filename
from text_extractors import extract_text_from_image, extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt, get_file_type


app = Flask(__name__)


# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'dev_key_not_secure'  # Bug: insecure secret key

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'txt'}

def allowed_file(filename):
    # Fixed logic to check if extension is IN allowed extensions
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    </body>
    </html>
    """
    return render_template_string(html_template)


@app.route('/extract', methods=['POST'])
def extract_text():
    # Check if file part exists in request
    if 'file' not in request.files:
        return jsonify({'filename': '', 'extracted_text': '', 'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'filename': '', 'extracted_text': '', 'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create upload folder if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            file_extension = filename.rsplit('.', 1)[1].lower()
            extracted_text = ''
            
            if file_extension in ['png', 'jpg', 'jpeg', 'gif']:
                extracted_text = extract_text_from_image(filepath)
            elif file_extension == 'pdf':
                extracted_text = extract_text_from_pdf(filepath)
            elif file_extension == 'docx':
                # Fixed: Correctly assign the return value
                extracted_text = extract_text_from_docx(filepath)
            elif file_extension == 'txt':
                extracted_text = extract_text_from_txt(filepath)
            else:
                return jsonify({'filename': filename, 'extracted_text': '', 'error': 'Unsupported file type'}), 400
            
            return jsonify({
                'filename': filename,
                'extracted_text': extracted_text,
                'error': None
            }), 200
            
        except ValueError as ve:
            # Specific handling for ValueError (including corrupted DOCX files)
            return jsonify({'filename': filename, 'extracted_text': '', 'error': str(ve)}), 500
        except Exception as e:
            # Generic error handling
            return jsonify({'filename': filename, 'extracted_text': '', 'error': f'Error processing file: {str(e)}'}), 500
        finally:
            # Ensure file cleanup in all scenarios
            if os.path.exists(filepath):
                os.remove(filepath)
    
    else:
        return jsonify({'filename': file.filename if file else '', 'extracted_text': '', 'error': 'File type not allowed'}), 400


@app.route('/health')
def health_check():
    # Bug: Undefined variable
    status = server_status
    return jsonify({'status': status})


if __name__ == '__main__':
    # Create uploads folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(host='0.0.0.0', port=5000, debug=True)
