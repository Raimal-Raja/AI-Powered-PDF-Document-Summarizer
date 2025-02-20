from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import tempfile
import file_handler
import summarizer as summarizer  # Use the simplified version

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    summary_text = db.Column(db.Text, nullable=False)

def save_summary(user_id, file_name, summary_text):
    summary = Summary(user_id=user_id, file_name=file_name, summary_text=summary_text)
    db.session.add(summary)
    db.session.commit()

def get_user_summaries(user_id):
    return Summary.query.filter_by(user_id=user_id).all()

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Fix: Change "sha256" to "pbkdf2:sha256"
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("upload_page"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

# @app.route("/", methods=["GET", "POST"])
# def upload_page():
#     if "user_id" not in session:
#         return redirect(url_for("login"))
    
#     error_message = None
    
#     if request.method == "POST":
#         if "files" not in request.files:
#             return render_template("upload.html", error="No files uploaded", user_summaries=get_user_summaries(session["user_id"]))
        
#         uploaded_files = request.files.getlist("files")
#         if not uploaded_files or uploaded_files[0].filename == '':
#             return render_template("upload.html", error="No files selected", user_summaries=get_user_summaries(session["user_id"]))
            
#         temp_dir = tempfile.mkdtemp()
#         extracted_texts = {}
#         errors = []
        
#         for file in uploaded_files:
#             try:
#                 file_path = os.path.join(temp_dir, file.filename)
#                 file.save(file_path)
                
#                 if file.filename.lower().endswith(".pdf"):
#                     text = file_handler.extract_text_from_pdf(file_path)
#                 elif file.filename.lower().endswith(".docx"):
#                     text = file_handler.extract_text_from_docx(file_path)
#                 elif file.filename.lower().endswith(".txt"):
#                     with open(file_path, "r", encoding="utf-8") as f:
#                         text = f.read()
#                 else:
#                     errors.append(f"Unsupported file format: {file.filename}")
#                     continue
                
#                 if text and not (isinstance(text, str) and text.startswith("Error:")):
#                     extracted_texts[file.filename] = text
#                 else:
#                     errors.append(f"Failed to extract text from {file.filename}: {text}")
#             except Exception as e:
#                 errors.append(f"Error processing {file.filename}: {str(e)}")
        
#         if not extracted_texts:
#             error_message = "Could not extract text from any of the uploaded files."
#             if errors:
#                 error_message += " Errors: " + " | ".join(errors)
#             return render_template("upload.html", error=error_message, user_summaries=get_user_summaries(session["user_id"]))
        
#         try:
#             summary_type = request.form.get("summary_type", "extractive")
#             summaries = summarizer.batch_summarization(
#                 extracted_texts, 
#                 summary_type=summary_type,
#                 num_sentences=int(request.form.get("num_sentences", 5)),
#                 max_length=int(request.form.get("max_length", 150))
#             )
            
#             for file_name, summary_text in summaries.items():
#                 save_summary(session["user_id"], file_name, summary_text)
            
#             return render_template("results.html", summaries=summaries, errors=errors if errors else None)
#         except Exception as e:
#             error_message = f"Error generating summaries: {str(e)}"
#             return render_template("upload.html", error=error_message, user_summaries=get_user_summaries(session["user_id"]))
    
#     user_summaries = get_user_summaries(session["user_id"])
#     return render_template("upload.html", user_summaries=user_summaries, error=error_message)




@app.route("/", methods=["GET", "POST"])
def upload_page():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    error_message = None
    dependency_warnings = []
    
    # Check for required dependencies
    if not file_handler.PYMUPDF_AVAILABLE:
        dependency_warnings.append("PDF processing requires PyMuPDF. Install with 'pip install PyMuPDF'")
    if not file_handler.DOCX2TXT_AVAILABLE:
        dependency_warnings.append("DOCX processing requires docx2txt. Install with 'pip install docx2txt'")
    
    if request.method == "POST":
        if "files" not in request.files:
            return render_template("upload.html", 
                                  error="No files uploaded", 
                                  warnings=dependency_warnings,
                                  user_summaries=get_user_summaries(session["user_id"]))
        
        uploaded_files = request.files.getlist("files")
        if not uploaded_files or uploaded_files[0].filename == '':
            return render_template("upload.html", 
                                  error="No files selected", 
                                  warnings=dependency_warnings,
                                  user_summaries=get_user_summaries(session["user_id"]))
            
        temp_dir = tempfile.mkdtemp()
        extracted_texts = {}
        errors = []
        
        for file in uploaded_files:
            try:
                file_path = os.path.join(temp_dir, file.filename)
                file.save(file_path)
                
                if file.filename.lower().endswith(".pdf"):
                    if not file_handler.PYMUPDF_AVAILABLE:
                        errors.append(f"Cannot process PDF {file.filename}: PyMuPDF not installed")
                        continue
                    text = file_handler.extract_text_from_pdf(file_path)
                elif file.filename.lower().endswith(".docx"):
                    if not file_handler.DOCX2TXT_AVAILABLE:
                        errors.append(f"Cannot process DOCX {file.filename}: docx2txt not installed")
                        continue
                    text = file_handler.extract_text_from_docx(file_path)
                elif file.filename.lower().endswith(".txt"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                else:
                    errors.append(f"Unsupported file format: {file.filename}")
                    continue
                
                if text and not (isinstance(text, str) and text.startswith("Error:")):
                    extracted_texts[file.filename] = text
                else:
                    errors.append(f"Failed to extract text from {file.filename}: {text}")
            except Exception as e:
                errors.append(f"Error processing {file.filename}: {str(e)}")
        
        if not extracted_texts:
            error_message = "Could not extract text from any of the uploaded files."
            if errors:
                error_message += " Errors: " + " | ".join(errors)
            return render_template("upload.html", 
                                  error=error_message, 
                                  warnings=dependency_warnings,
                                  user_summaries=get_user_summaries(session["user_id"]))
        
        try:
            summary_type = request.form.get("summary_type", "extractive")
            summaries = summarizer.batch_summarization(
                extracted_texts, 
                summary_type=summary_type,
                num_sentences=int(request.form.get("num_sentences", 5)),
                max_length=int(request.form.get("max_length", 150))
            )
            
            for file_name, summary_text in summaries.items():
                save_summary(session["user_id"], file_name, summary_text)
            
            return render_template("results.html", 
                                  summaries=summaries, 
                                  warnings=dependency_warnings,
                                  errors=errors if errors else None)
        except Exception as e:
            error_message = f"Error generating summaries: {str(e)}"
            return render_template("upload.html", 
                                  error=error_message, 
                                  warnings=dependency_warnings,
                                  user_summaries=get_user_summaries(session["user_id"]))
    
    user_summaries = get_user_summaries(session["user_id"])
    return render_template("upload.html", 
                          user_summaries=user_summaries, 
                          warnings=dependency_warnings,
                          error=error_message)
# FIX: Create a proper app context for database initialization
def initialize_database():
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()  # Initialize DB in app context
    app.run(debug=True)