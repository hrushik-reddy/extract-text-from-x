# Extract Text from X

A Flask web application that extracts text from various file formats including images, PDFs, and DOCX files.

## Features

- **Image Text Extraction**: Extract text from images (PNG, JPG, JPEG, GIF) using OCR (Tesseract)
- **PDF Text Extraction**: Extract text from PDF files using PyMuPDF and PyPDF2 as fallback
- **DOCX Text Extraction**: Extract text from Microsoft Word documents
- **Web Interface**: Simple HTML form for file uploads
- **REST API**: JSON API endpoints for programmatic access

## Installation

### Prerequisites

- Python 3.7+
- Tesseract OCR engine

#### Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd extract-text-from-x
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create uploads directory:
```bash
mkdir uploads
```

## Usage

### Start the Flask Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Select a file (image, PDF, or DOCX)
3. Click "Extract Text" to process the file
4. View the extracted text in JSON format

### API Endpoints

#### Extract Text from File
- **URL**: `/extract`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**: 
  - `file`: The file to extract text from

**Example using curl:**
```bash
curl -X POST -F "file=@sample.pdf" http://localhost:5000/extract
```

#### Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Response**: Server health status

## Supported File Formats

- **Images**: PNG, JPG, JPEG, GIF, BMP, TIFF
- **Documents**: PDF, DOCX
- **Text**: TXT

## File Size Limits

- Maximum file size: 16MB
- This can be configured in `app.py` by modifying `MAX_CONTENT_LENGTH`

## Configuration

Key configuration options in `app.py`:

- `UPLOAD_FOLDER`: Directory for temporary file storage
- `MAX_CONTENT_LENGTH`: Maximum allowed file size
- `ALLOWED_EXTENSIONS`: Supported file extensions

## Error Handling

The application includes error handling for:
- Unsupported file types
- File processing errors
- Missing files
- Server errors

## Development

### Project Structure
```
extract-text-from-x/
├── app.py                 # Flask application
├── text_extractors.py     # Text extraction functions
├── requirements.txt       # Python dependencies
├── uploads/              # Temporary file storage
└── README.md             # This file
```

### Adding New File Types

To add support for new file types:

1. Add the extension to `ALLOWED_EXTENSIONS` in `app.py`
2. Create a new extraction function in `text_extractors.py`
3. Add the logic to handle the new file type in the `/extract` route

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract OCR is properly installed and in your PATH
2. **Permission errors**: Check that the uploads directory has proper write permissions
3. **Memory issues**: Large files may cause memory issues; consider implementing streaming for large files

### Debug Mode

The application runs in debug mode by default. To disable:
```python
app.run(debug=False)
```

## Security Considerations

- The application uses a development secret key
- File uploads are not extensively validated
- Consider implementing authentication for production use
- Implement proper file type validation beyond extensions

## License

This project is for educational/testing purposes.