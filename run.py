from flask import Flask, request, jsonify, url_for,render_template
from werkzeug.utils import secure_filename
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024  # Limit file size to 16 MB

max_size = 5 * 1024 * 1024
# In-memory store for upload sessions
upload_sessions = {}
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/request-upload-session', methods=['POST'])
def request_upload_session():
    session_id = str(uuid.uuid4())  # Generate a unique session ID
    upload_sessions[session_id] = {
        'url': url_for('upload_file', session_id=session_id, _external=True)
    }
    return jsonify({
        'session_id': session_id,
        'upload_url': upload_sessions[session_id]['url']
    })

@app.route('/upload/<session_id>', methods=['POST'])
def upload_file(session_id):
    if session_id not in upload_sessions:
        return 'Invalid session ID', 400
    if 'files' not in request.files:
        return 'No files part', 400
    file_size = 0
    files = request.files.getlist('files')
    if not files:
        return 'No files selected', 400
    
    saved_files = []
    for file in files:
        if file.filename == '':
            continue
        filename = file.filename
            # Read the file in chunks
        chunk_size = 1024 * 1024  # 1 MB chunks
        while True:
            chunk = file.stream.read(chunk_size)
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > max_size:
                return 'File too large', 413
        file.seek(0)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        saved_files.append(filename)
    
    if saved_files:
        return f'Files successfully uploaded: {", ".join(saved_files)}'
    else:
        return 'No valid files to upload', 400


def check_disk_permissions(path):
    
    if not os.path.exists(path):
        return False
    
    read_permission = os.access(path, os.R_OK)
    write_permission = os.access(path, os.W_OK)

    if read_permission and write_permission:
        return True
    return False

def check_env():
    if not os.getenv('MAX_FILE_UPLOAD'):
        print("Max file upload not set")
        return False
    if not os.getenv('MAX_FILE_UPLOAD').isdigit():
        print("Only input digit in MAX_FILE_UPLOAD")
        return False
    if not check_disk_permissions(os.getenv('UPLOAD_FOLDER')):
        print("Can't access upload folder")
        return False
    return True

if __name__ == '__main__':
    if (check_env()):
        app.run(debug=True)
