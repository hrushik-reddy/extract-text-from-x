from flask import Flask, request, jsonify, render_template_string
import os
from werkzeug.utils import secure_filename
from text_extractors import extract_text_from_image, extract_text_from_pdf, extract_text_from_docx

app = Flask(__name__)

# Configuration with deliberate issues
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'dev_key_not_secure'  # Bug: insecure secret key

# Bug: Missing allowed extensions configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}

def allowed_file(filename):
    # Bug: Logic error - should check if extension is IN allowed extensions
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS

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
    # Bug: No error handling for missing file
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Bug: Using the buggy allowed_file function
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Bug: Not checking if upload folder exists
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Bug: Wrong variable name - should be 'filepath' not 'file_path'
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            if file_extension in ['png', 'jpg', 'jpeg', 'gif']:
                # Bug: Using wrong variable name
                extracted_text = extract_text_from_image(file_path)
            elif file_extension == 'pdf':
                extracted_text = extract_text_from_pdf(filepath)
            elif file_extension == 'docx':
                # Bug: Missing variable assignment
                extract_text_from_docx(filepath)
            else:
                return jsonify({'error': 'Unsupported file type'}), 400
            
            # Bug: Trying to delete file before returning response, but using wrong path
            os.remove(file_path)
            
            return jsonify({
                'filename': filename,
                'extracted_text': extracted_text
            })
            
        except Exception as e:
            # Bug: Not cleaning up file on error
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/health')
def health_check():
    # Bug: Undefined variable
    status = server_status
    return jsonify({'status': status})

# Bug: Missing main guard and incorrect debug parameter
if __name__ == '__main__':
    # Bug: uploads folder not created if it doesn't exist
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)  # Bug: threaded=False can cause issues