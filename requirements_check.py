#!/usr/bin/env python3
"""
Requirements check script for Document Summarizer application
Run this script to diagnose installation and compatibility issues
"""

import sys
import platform
import pkg_resources
import importlib.util

def print_system_info():
    """Print basic system and Python information"""
    print("\n" + "="*50)
    print(f"SYSTEM INFORMATION:")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")
    if platform.system() == "Windows":
        print(f"Windows version: {platform.win32_ver()[0]}")
    print("="*50 + "\n")

def check_package(package_name):
    """Check if a package is installed and get its version"""
    try:
        package = pkg_resources.get_distribution(package_name)
        return True, package.version
    except pkg_resources.DistributionNotFound:
        return False, None

def check_file_processing_deps():
    """Check dependencies for file processing"""
    print("\nFILE PROCESSING DEPENDENCIES:")
    
    # Check PyMuPDF
    pymupdf_installed, pymupdf_version = check_package("pymupdf")
    if pymupdf_installed:
        print(f"✅ PyMuPDF (fitz) v{pymupdf_version} - PDF extraction available")
    else:
        print("❌ PyMuPDF not found - PDF extraction will be unavailable")
        print("   Install with: pip install pymupdf")

    # Check docx processors
    docx2txt_installed, docx2txt_version = check_package("docx2txt")
    python_docx_installed, python_docx_version = check_package("python-docx")
    
    if docx2txt_installed:
        print(f"✅ docx2txt v{docx2txt_version} - DOCX extraction available")
    elif python_docx_installed:
        print(f"✅ python-docx v{python_docx_version} - DOCX extraction available (fallback)")
    else:
        print("❌ No DOCX processor found - DOCX extraction will be unavailable")
        print("   Install with: pip install docx2txt")

def check_summarization_deps():
    """Check dependencies for summarization"""
    print("\nSUMMARIZATION DEPENDENCIES:")
    
    # Check sumy
    sumy_installed, sumy_version = check_package("sumy")
    if sumy_installed:
        print(f"✅ sumy v{sumy_version} - Extractive summarization available")
    else:
        print("❌ sumy not found - Extractive summarization will be unavailable")
        print("   Install with: pip install sumy")
    
    # Check transformers
    transformers_installed, transformers_version = check_package("transformers")
    torch_installed, torch_version = check_package("torch")
    
    if transformers_installed and torch_installed:
        print(f"✅ transformers v{transformers_version} with PyTorch v{torch_version}")
        
        # Check GPU availability if torch is installed
        import_torch = importlib.util.find_spec("torch")
        if import_torch:
            try:
                import torch
                if torch.cuda.is_available():
                    print(f"✅ GPU acceleration available - {torch.cuda.get_device_name(0)}")
                else:
                    print("⚠️ GPU acceleration unavailable - using CPU only (slower)")
            except Exception as e:
                print(f"⚠️ Error checking GPU: {str(e)}")
    elif transformers_installed:
        print(f"⚠️ transformers v{transformers_version} found but PyTorch missing")
        print("   Install PyTorch with: pip install torch")
    else:
        print("❌ transformers not found - Abstractive summarization will be unavailable")
        print("   Install with: pip install transformers torch")

def check_web_app_deps():
    """Check dependencies for web application"""
    print("\nWEB APPLICATION DEPENDENCIES:")
    
    flask_installed, flask_version = check_package("flask")
    sqlalchemy_installed, sqlalchemy_version = check_package("flask-sqlalchemy")
    
    if flask_installed:
        print(f"✅ Flask v{flask_version}")
    else:
        print("❌ Flask not found - Web application will not run")
        print("   Install with: pip install flask")
    
    if sqlalchemy_installed:
        print(f"✅ Flask-SQLAlchemy v{sqlalchemy_version}")
    else:
        print("❌ Flask-SQLAlchemy not found - Database functionality will not work")
        print("   Install with: pip install flask-sqlalchemy")

def check_module_imports():
    """Try importing key modules to verify they can be loaded"""
    print("\nMODULE IMPORT TESTS:")
    
    modules_to_test = {
        "File Handler": [
            ("fitz", "PyMuPDF for PDF processing"),
            ("docx2txt", "DOCX text extraction")
        ],
        "Summarizer": [
            ("sumy.summarizers.text_rank", "TextRank summarizer"),
            ("transformers", "Hugging Face Transformers")
        ],
        "Web App": [
            ("flask", "Flask web framework"),
            ("flask_sqlalchemy", "SQLAlchemy database integration")
        ]
    }
    
    for category, modules in modules_to_test.items():
        print(f"\n  {category} modules:")
        for module_name, description in modules:
            try:
                # Try to import the module
                spec = importlib.util.find_spec(module_name)
                if spec is not None:
                    print(f"    ✅ Successfully imported {module_name} ({description})")
                else:
                    print(f"    ❌ Failed to find {module_name} ({description})")
            except ImportError as e:
                print(f"    ❌ Error importing {module_name}: {str(e)}")

def check_compatibility_issues():
    """Check for known compatibility issues with different Python versions"""
    print("\nCOMPATIBILITY CHECK:")
    
    python_version = sys.version_info
    
    # Python 3.12 compatibility issues
    if python_version.major == 3 and python_version.minor >= 12:
        print(f"⚠️ Python {python_version.major}.{python_version.minor} detected.")
        print("   Known compatibility issues with Python 3.12:")
        print("   - Some older versions of PyMuPDF may not work with Python 3.12")
        print("   - Some transformers models might have compatibility issues")
        print("   - SQLAlchemy older than 2.0 may show deprecation warnings")
        print("\n   Recommended solution: Use Python 3.10 or install latest package versions")
    
    # Python version too old
    if python_version.major == 3 and python_version.minor < 8:
        print(f"⚠️ Python {python_version.major}.{python_version.minor} is older than recommended.")
        print("   Some modern libraries may not support this Python version.")
        print("   Recommended: Use Python 3.8 or newer.")

def print_installation_instructions():
    """Print instructions for installing all required packages"""
    print("\n" + "="*50)
    print("INSTALLATION INSTRUCTIONS")
    print("="*50)
    print("\nTo install all required dependencies, run the following commands:")
    
    print("\n# Basic web application dependencies")
    print("pip install flask flask-sqlalchemy")
    
    print("\n# File processing dependencies")
    print("pip install pymupdf docx2txt")
    
    print("\n# Summarization dependencies")
    print("pip install sumy nltk transformers torch")
    
    print("\n# Initialize NLTK data (required for sumy)")
    print("python -c \"import nltk; nltk.download('punkt')\"")
    
    print("\n# All dependencies in one command")
    print("pip install flask flask-sqlalchemy pymupdf docx2txt sumy nltk transformers torch")
    print("="*50)

if __name__ == "__main__":
    print("\n🔍 DOCUMENT SUMMARIZER APPLICATION - REQUIREMENTS CHECK 🔍")
    print_system_info()
    check_file_processing_deps()
    check_summarization_deps() 
    check_web_app_deps()
    check_module_imports()
    check_compatibility_issues()
    print_installation_instructions()
    
    print("\n✨ Requirements check complete! ✨")