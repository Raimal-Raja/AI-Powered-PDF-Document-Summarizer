from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import sys
import subprocess

# Check and install required packages
def install_required_packages():
    """Check and install required packages before execution."""
    required_packages = ['pdfminer.six', 'python-docx']
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            print(f"Attempting to install {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"{package} installed successfully.")
            except Exception as e:
                print(f"Error installing {package}: {str(e)}")

# Install required packages before importing them
install_required_packages()

import file_handler
import summarizer

# Create the templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_EXTENSIONS'] = ['.pdf', '.docx', '.txt']

# Ensure instance directory exists
if not os.path.exists('instance'):
    os.makedirs('instance')

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
        else:
            flash("Invalid username or password", "error")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
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
    flash("You have been logged out", "info")
    return redirect(url_for("login"))

def allowed_file(filename):
    return '.' in filename and \
           os.path.splitext(filename)[1].lower() in app.config['UPLOAD_EXTENSIONS']

@app.route("/", methods=["GET", "POST"])
def upload_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        summary_type = request.form.get("summary_type", "extractive")
        num_sentences = int(request.form.get("num_sentences", 5) or 5)
        max_length = int(request.form.get("max_length", 150) or 150)

        if "file" not in request.files:
            flash("No file selected", "error")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No file selected", "error")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(app.instance_path, 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

            text = None
            summary_text = None

            try:
                if filename.lower().endswith('.pdf'):
                    text = file_handler.extract_text_from_pdf(file_path)
                elif filename.lower().endswith('.docx'):
                    text = file_handler.extract_text_from_docx(file_path)
                elif filename.lower().endswith('.txt'):
                    text = file_handler.extract_text_from_txt(file_path)
                else:
                    flash("Unsupported file type", "error")
                    return redirect(request.url)

                # Debug: Log extracted text length
                print(f"Extracted text length: {len(text) if text else 0}")

                # Validate extracted text
                if not text or text.startswith("Error") or "Error" in text or len(text.strip()) < 10:
                    flash(f"Text extraction failed: {text[:300]}...", "error")
                    return redirect(request.url)

                # Debug: Print first 300 characters of extracted text
                print(f"First 300 chars of extracted text: {text[:300]}")

                # Generate summary
                if summary_type == "abstractive":
                    summary_text = summarizer.abstractive_summary(text, max_length)
                else:
                    summary_text = summarizer.extractive_summary(text, num_sentences)

                # Debug: Print first 300 characters of summary
                print(f"First 300 chars of generated summary: {summary_text[:300] if summary_text else 'None'}")

                # Check summary validity
                if not summary_text or len(summary_text.strip()) < 10:
                    flash("Generated summary is too short or empty.", "error")
                    return redirect(request.url)

                # Save summary to database
                new_summary = Summary(
                    user_id=session["user_id"],
                    file_name=filename,
                    summary_text=summary_text
                )
                db.session.add(new_summary)
                db.session.commit()

                flash("File processed successfully!", "success")
                return render_template("results.html", summary=summary_text, filename=filename)

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Error processing file: {str(e)}")
                print(f"Traceback: {error_trace}")
                flash(f"Error processing file: {str(e)}", "error")
                return redirect(request.url)

        else:
            flash("Unsupported file type", "error")
            return redirect(request.url)

    return render_template("upload.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(413)
def file_too_large(e):
    flash("File too large. Maximum size is 16MB.", "error")
    return redirect(url_for('upload_page'))

def create_demo_user():
    """Create a demo user if no users exist"""
    if not User.query.first():
        demo_user = User(
            username="demo",
            password=generate_password_hash("demo123")
        )
        db.session.add(demo_user)
        db.session.commit()
        print("Demo user created - Username: demo, Password: demo123")

def initialize_database():
    """Initialize the database and create tables"""
    with app.app_context():
        db.create_all()
        create_demo_user()
        print("Database initialized successfully!")

def create_template_files():
    """Create template files if they don't exist"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # List of template files that should exist
    template_files = ['base.html', 'login.html', 'register.html', 'upload.html', 'results.html']
    
    for template in template_files:
        template_path = os.path.join(templates_dir, template)
        if not os.path.exists(template_path):
            with open(template_path, 'w') as f:
                f.write('<!-- Template file created by initialization -->')
            print(f"Created template file: {template}")

if __name__ == "__main__":
    try:
        # Initialize everything
        initialize_database()
        create_template_files()
        
        # Start the Flask application
        print("Starting Flask application...")
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        sys.exit(1)