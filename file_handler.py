import os
import traceback

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    print("WARNING: pdfplumber not available. Install with 'pip install pdfplumber'.")
    PDFPLUMBER_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    print("WARNING: python-docx not available. Install with 'pip install python-docx'.")
    DOCX_AVAILABLE = False

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber."""
    if not PDFPLUMBER_AVAILABLE:
        return "Error: pdfplumber required. Install with 'pip install pdfplumber'."
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text if text.strip() else "Error: No extractable text in PDF."
    except Exception as e:
        return f"Error extracting PDF {pdf_path}: {str(e)}"

def extract_text_from_docx(docx_path):
    """Extract text from DOCX using python-docx."""
    if not DOCX_AVAILABLE:
        return "Error: python-docx required. Install with 'pip install python-docx'."
    
    try:
        doc = Document(docx_path)
        text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        return text if text.strip() else "Error: No extractable text in DOCX."
    except Exception as e:
        return f"Error extracting DOCX {docx_path}: {str(e)}"

def extract_text_from_txt(txt_path):
    """Extract text from TXT with robust encoding handling."""
    encodings = ['utf-8', 'latin-1', 'utf-16']
    for encoding in encodings:
        try:
            with open(txt_path, "r", encoding=encoding) as file:
                return file.read().strip()
        except Exception:
            continue
    return f"Error extracting TXT {txt_path}: All encoding attempts failed."

def batch_extract_text(folder_path):
    """Extract text from all files in a folder."""
    extracted_texts = {}
    if not os.path.exists(folder_path):
        return {"error": f"Folder not found: {folder_path}"}
    
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if not os.path.isfile(file_path):
            continue
        
        try:
            if file_name.lower().endswith(".pdf"):
                extracted_texts[file_name] = extract_text_from_pdf(file_path)
            elif file_name.lower().endswith(".docx"):
                extracted_texts[file_name] = extract_text_from_docx(file_path)
            elif file_name.lower().endswith(".txt"):
                extracted_texts[file_name] = extract_text_from_txt(file_path)
        except Exception as e:
            extracted_texts[file_name] = f"Error processing {file_name}: {str(e)}"
            print(f"Error: {traceback.format_exc()}")
    
    return extracted_texts