import os
import traceback

# Try to import PyMuPDF, but provide fallback
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    print("WARNING: PyMuPDF not available. PDF extraction will be limited.")
    PYMUPDF_AVAILABLE = False

# Try to import docx2txt
try:
    import docx2txt
    DOCX2TXT_AVAILABLE = True
except ImportError:
    print("WARNING: docx2txt not available. DOCX extraction will be limited.")
    DOCX2TXT_AVAILABLE = False

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file, handling errors gracefully."""
    if not PYMUPDF_AVAILABLE:
        return "Error: PyMuPDF is required. Install it with 'pip install pymupdf'."

    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text() for page in doc])
        return text if text.strip() else "Error: No extractable text found in PDF."
    except Exception as e:
        return f"Error extracting text from PDF {pdf_path}: {str(e)}"

def extract_text_from_docx(docx_path):
    """Extract text from DOCX with robust error handling"""
    if not DOCX2TXT_AVAILABLE:
        return f"Error: docx2txt not available. Cannot extract text from {docx_path}"
    
    try:
        return docx2txt.process(docx_path)
    except Exception as e:
        error_msg = f"Error extracting text from DOCX {docx_path}: {str(e)}"
        print(error_msg)
        return error_msg

def extract_text_from_txt(txt_path):
    """Extract text from TXT with robust error handling"""
    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encodings if UTF-8 fails
        try:
            with open(txt_path, "r", encoding="latin-1") as file:
                return file.read()
        except Exception as e:
            error_msg = f"Error extracting text from TXT {txt_path}: {str(e)}"
            print(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error extracting text from TXT {txt_path}: {str(e)}"
        print(error_msg)
        return error_msg

def batch_extract_text(folder_path):
    """Extract text from all supported files in a folder"""
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
            print(f"Error processing {file_name}: {traceback.format_exc()}")
            
    return extracted_texts