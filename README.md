# Document Summarizer Web Application

![GitHub License](https://img.shields.io/github/license/xAI/DocSummarizer?style=flat-square)
![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.x-green.svg?style=flat-square)

Welcome to the **Document Summarizer Web Application**, a lightweight, open-source tool for extracting and summarizing text from PDF, DOCX, and TXT files. Built with Python, Flask, and NLTK, this project supports both extractive and abstractive summarization, offering a user-friendly web interface with user authentication, persistent storage, and robust offline capabilities. It uses free, open-source libraries like `pdfplumber` and `python-docx` for file handling, making it accessible and efficient for local use.

## Features
- **Text Extraction**: Seamlessly handles PDF, DOCX, and TXT files using `pdfplumber`, `python-docx`, and robust file reading with encoding fallbacks.
- **Summarization Types**:
  - **Extractive**: Selects key sentences based on word frequency, excluding common stopwords for relevance.
  - **Abstractive**: Generates concise summaries by combining and truncating key sentences (simplified, lightweight approach for offline use).
- **User Authentication**: Secure login and registration with Flask-SQLAlchemy and SQLite for user management.
- **Persistent Storage**: Stores summaries in a local SQLite database, allowing users to view previous summaries offline.
- **Responsive UI**: Features a clean, mobile-friendly interface built with Bootstrap 5, including a copy-to-clipboard function for summaries.
- **Offline Capability**: Operates entirely offline after initial setup, requiring no internet connection for summarization once dependencies and resources are installed locally.
- **Error Handling**: Robustly manages file format errors, encoding issues, missing dependencies, and NLTK resource failures with clear user feedback.

## Installation

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package installer)

### Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/Raimal-Raja/AI-Powered-PDF-Document-Summarizer.git
   cd AI-Powered-PDF-Document-Summarizer
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   The app automatically installs required packages (`nltk`, `pdfplumber`, `python-docx`, `flask`, `flask-sqlalchemy`) on first run, but you can manually install them:
   ```bash
   pip install flask flask-sqlalchemy nltk pdfplumber python-docx
   ```

4. Download NLTK resources (required for offline use):
   Run the following in Python to manually download `punkt` and `stopwords`:
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   ```
   Alternatively, the app will attempt to download these resources automatically during startup, but an internet connection is needed initially.

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://127.0.0.1:5000`. Use the demo credentials `Raimal/Raimal123` to log in and start summarizing documents.

## Usage
- **Upload a File**: Use the web interface to upload PDF, DOCX, or TXT files from your local machine.
- **Select Summarization Type**: Choose between extractive (key sentences) or abstractive summarization, and adjust parameters like the number of sentences or maximum summary length.
- **View Results**: See the generated summary on the results page, with options to copy it to your clipboard or return to upload more documents.
- **Previous Summaries**: View past summaries on the upload page, accessible offline after storage in the local database.

## Offline Capabilities
This project is designed to work offline after initial setup, making it ideal for use in environments without internet access. Here’s how to ensure offline functionality:
- **Pre-Download Dependencies**: Install all Python packages and NLTK resources (`punkt`, `stopwords`) with an internet connection.
- **Local Storage**: Files are processed locally, and summaries are stored in a SQLite database (`app.db`) in the `instance` directory.
- **No External APIs**: The summarization and text extraction logic rely solely on local libraries and pre-downloaded resources, avoiding cloud dependencies.
- **NLTK Resource Management**: Ensure the `nltk_data` directory (containing `tokenizers/punkt` and `corpora/stopwords`) is copied to the project directory or user home directory for offline access. Use `nltk.data.path` to verify the location.
- **Testing Offline**: After setup, disconnect from the internet, run `python app.py`, and test uploading files to confirm summarization works without connectivity.

## Project Structure
```
DocSummarizer/
├── instance/
│   ├── uploads/           # Directory for uploaded files
│   └── app.db             # SQLite database for users and summaries
├── templates/
│   ├── 404.html           # Error page template
│   ├── base.html          # Base HTML template
│   ├── login.html         # Login page template
│   ├── register.html      # Registration page template
│   ├── results.html       # Summary results page template
│   └── upload.html        # Upload and summary history page template
├── app.py                 # Flask web application
├── file_handler.py        # Text extraction logic for PDF, DOCX, and TXT
└── summarizer.py          # Summarization algorithms (extractive and abstractive)
```

## Algorithms and Logic
- **Text Extraction**:
  - Uses `pdfplumber` to parse PDFs, `python-docx` for DOCX files, and file reading with encoding fallbacks (UTF-8, Latin-1, UTF-16) for TXT files.
- **Extractive Summarization**:
  - Preprocesses text, tokenizes sentences with NLTK’s `sent_tokenize` (or falls back to period-based splitting), analyzes word frequencies (excluding stopwords), scores sentences, and selects the top N sentences by relevance.
- **Abstractive Summarization**:
  - Leverages extractive summarization to pick key sentences, combines them, and truncates to a specified length, offering a lightweight alternative to complex NLP models.
- For a detailed explanation, refer to the code comments in `summarizer.py` or the [project documentation](#references-and-resources).

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository and create a branch for your changes.
2. Install dependencies as described above.
3. Write tests for new features or bug fixes (if applicable).
4. Update documentation and README as needed.
5. Submit a pull request with a clear description of your changes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References and Resources
- **NLTK Documentation**: [Natural Language Toolkit (NLTK)](https://www.nltk.org/) – Used for tokenization and stopwords, essential for summarization logic.
- **Flask Documentation**: [Flask Web Framework](https://flask.palletsprojects.com/) – Core framework for the web application.
- **pdfplumber**: [pdfplumber on GitHub](https://github.com/jsvine/pdfplumber) – Lightweight PDF text extraction library.
- **python-docx**: [python-docx on PyPI](https://pypi.org/project/python-docx/) – Library for reading DOCX files.
- **Bootstrap 5**: [Bootstrap Documentation](https://getbootstrap.com/docs/5.1/getting-started/introduction/) – CSS framework for the UI.
- **Summarization Techniques**: [Extractive vs. Abstractive Summarization](https://towardsdatascience.com/extractive-vs-abstractive-summarization-understanding-the-difference-5b7e24f1c2a7) – Theoretical background on summarization methods.
- **SQLite with Flask**: [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/) – Integration for local database management.
- **Offline NLP Tools**: [Offline NLP with Python](https://realpython.com/nlp-python/) – Guidance on using NLP libraries offline.

## Acknowledgments
- Inspired by the open-source NLP and web development communities.
- Special thanks to the maintainers of NLTK, Flask, `pdfplumber`, `python-docx`, and Bootstrap for their invaluable tools.

## Issues and Support
If you encounter any issues, please open an issue on [GitHub Issues](https://github.com/Raimal-Raja/AI-Powered-PDF-Document-Summarizer/issues) with detailed reproduction steps. For feature requests or questions, contact the maintainers via email or pull requests.
.
