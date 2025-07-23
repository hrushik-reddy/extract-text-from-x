import pytesseract
from PIL import Image
import PyPDF2
import fitz  # PyMuPDF
from docx import Document
import os

def extract_text_from_image(image_path):
    """
    Extract text from image using OCR (Tesseract)
    """
    try:
        # Open image using PIL
        image = Image.open(image_path)
        
        # Use pytesseract to extract text
        extracted_text = pytesseract.image_to_string(image)
        
        return extracted_text.strip()
    
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using PyMuPDF (fitz)
    """
    try:
        text = ""
        
        # Open PDF document
        pdf_document = fitz.open(pdf_path)
        
        # Iterate through pages
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        
        pdf_document.close()
        return text.strip()
    
    except Exception as e:
        # Fallback to PyPDF2
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            
            return text.strip()
            
        except Exception as e2:
            raise Exception(f"Error extracting text from PDF: {str(e2)}")

def extract_text_from_docx(docx_path):
    """
    Extract text from DOCX file
    """
    try:
        # Open document
        doc = Document(docx_path)
        
        # Extract text from paragraphs
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + "\t"
                text += "\n"
        
        return text.strip()
    
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")

def extract_text_from_txt(txt_path):
    """
    Extract text from plain text file
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(txt_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")
    except Exception as e:
        raise Exception(f"Error extracting text from TXT: {str(e)}")

def get_file_type(filename):
    """
    Get file type from filename
    """
    if '.' not in filename:
        return None
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    file_types = {
        'png': 'image',
        'jpg': 'image',
        'jpeg': 'image',
        'gif': 'image',
        'bmp': 'image',
        'tiff': 'image',
        'pdf': 'pdf',
        'docx': 'docx',
        'txt': 'txt'
    }
    
    return file_types.get(extension, 'unknown')