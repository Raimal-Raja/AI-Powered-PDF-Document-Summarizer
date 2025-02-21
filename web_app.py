from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import sys
import subprocess
import traceback

def install_required_packages():
    """Install required packages."""
    packages = ['nltk', 'pdfplumber', 'python-docx']
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} installed.")

install_required_packages()

import file_handler
import summarizer

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.pdf', '.docx', '.txt']

os.makedirs('instance', exist_ok=True)
os.makedirs('templates', exist_ok=True)

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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("upload_page"))
        flash("Invalid credentials", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))
        if User.query.filter_by(username=username).first():
            flash("Username exists", "error")
            return redirect(url_for("register"))
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out", "info")
    return redirect(url_for("login"))

def allowed_file(filename):
    return '.' in filename and os.path.splitext(filename)[1].lower() in app.config['UPLOAD_EXTENSIONS']

@app.route("/", methods=["GET", "POST"])
def upload_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    summaries = Summary.query.filter_by(user_id=session["user_id"]).all()

    if request.method == "POST":
        summary_type = request.form.get("summary_type", "extractive")
        num_sentences = int(request.form.get("num_sentences", 5) or 5)
        max_length = int(request.form.get("max_length", 150) or 150)

        if "file" not in request.files or not request.files["file"].filename:
            flash("No file selected", "error")
            return redirect(request.url)

        file = request.files["file"]
        if not allowed_file(file.filename):
            flash("Unsupported file type", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        upload_dir = os.path.join(app.instance_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        text = None
        if filename.endswith('.pdf'):
            text = file_handler.extract_text_from_pdf(file_path)
        elif filename.endswith('.docx'):
            text = file_handler.extract_text_from_docx(file_path)
        elif filename.endswith('.txt'):
            text = file_handler.extract_text_from_txt(file_path)

        print(f"Extracted text (first 300 chars): {text[:300] if text else 'None'}")
        if not text or text.startswith("Error") or len(text.strip()) < 20:
            flash(f"Text extraction failed: {text[:100] if text else 'No text'}...", "error")
            return redirect(request.url)

        try:
            if summary_type == "abstractive":
                summary_text = summarizer.abstractive_summary(text, max_length)
            else:
                summary_text = summarizer.extractive_summary(text, num_sentences)
            
            print(f"Summary (first 300 chars): {summary_text[:300] if summary_text else 'None'}")
            if not summary_text or summary_text.startswith("No valid") or len(summary_text.strip()) < 20:
                flash(f"Summary generation failed: {summary_text[:100] if summary_text else 'No summary'}...", "error")
                return redirect(request.url)

            new_summary = Summary(user_id=session["user_id"], file_name=filename, summary_text=summary_text)
            db.session.add(new_summary)
            db.session.commit()

            summaries_dict = {filename: summary_text}
            flash("File processed successfully!", "success")
            return render_template("results.html", summaries=summaries_dict, filename=filename)

        except Exception as e:
            print(f"Error processing file: {str(e)}\n{traceback.format_exc()}")
            flash(f"Error generating summary: {str(e)}", "error")
            return redirect(request.url)

    return render_template("upload.html", summaries=summaries)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(413)
def file_too_large(e):
    flash("File too large (max 16MB)", "error")
    return redirect(url_for('upload_page'))

def initialize_database():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            demo_user = User(username="demo", password=generate_password_hash("demo123"))
            db.session.add(demo_user)
            db.session.commit()
            print("Demo user created: demo/demo123")

if __name__ == "__main__":
    try:
        initialize_database()
        print("Starting Flask app...")
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Error starting app: {str(e)}")
        sys.exit(1)