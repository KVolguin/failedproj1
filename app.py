from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "app.db")}' # Creates absolute path for app.py to be created
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# File Upload Configuration
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the directory exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Include a Model for database
class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"<UploadedFile {self.filename}>"

# Routes
@app.route('/api/files', methods=['GET'])
def get_files():
    files = UploadedFile.query.all()
    result = [
        {
            "id": file.id, 
            "filename": file.filename, 
            "filepath": file.filepath, 
            "uploaded_at": file.uploaded_at
        }
        for file in files
    ]
    return jsonify(result)

@app.route('/api/process', methods=['POST'])
def process():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    return jsonify({"received": data}), 200

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Save file details to the database
    uploaded_file = UploadedFile(filename=filename, filepath=filepath)
    db.session.add(uploaded_file)
    db.session.commit()

    return jsonify({"message": f"File uploaded successfully: {filename}"}), 200

@app.route('/')
def home():
    return 'Hello, Flask!'

@app.route('/about')
def about():
    return 'This is the About page!'

if __name__ == "__main__":
    app.run(debug=True)
