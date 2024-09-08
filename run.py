from flask import Flask, request, jsonify, url_for,render_template
from werkzeug.utils import secure_filename
import os
import uuid
from dotenv import load_dotenv

load_dotenv('.env')

app = Flask(__name__)
max_size = 5 * 1024 * 1024

allowed_ext = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload/', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify(
            msg = 'No files part'
        ), 400
    file_size = 0
    files = request.files.getlist('files')
    if not files:
        return jsonify(
            msg = 'No files selected'
        ), 400
    
    saved_files = []
    for file in files:
        if file.filename == '':
            continue
        filename = secure_filename(file.filename)
        if not allowed_file(filename):
            return jsonify(
                msg = "Invalid file type"
            ),415
        # Read the file in chunks
        chunk_size = 1024 * 1024  # 1 MB chunks
        while True:
            chunk = file.stream.read(chunk_size)
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > max_size:
                return jsonify(
                    msg = 'File too large.'
                ), 413
        file.seek(0)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        saved_files.append(filename)
    
    if saved_files:
        # return f'Files successfully uploaded: {", ".join(saved_files)}'
        return jsonify(
            saved_files
        )
    else:
        return jsonify(
            msg = 'No valid files to upload.'
        ), 400


def check_disk_permissions(path):
    
    if not os.path.exists(path):
        return False
    
    read_permission = os.access(path, os.R_OK)
    write_permission = os.access(path, os.W_OK)

    if read_permission and write_permission:
        return True
    return False

def check_env():
    if os.getenv('DB_NAME'):
        if os.getenv('MAX_LENGTH'):
            if os.getenv('MAX_LENGTH').isdigit():
                if check_disk_permissions(os.getenv('UPLOAD_FOLDER')):
                    return True 
                print("Can't access upload folder")
                return False
            print("Only input digit in MAX_LENGTH")
            return False 
        print("MAX_LENGTH not set")
        return False
    print('DB_NAME not set')
    return False


if __name__ == '__main__':
    if (check_env()):
        app.config['SECRET_KEY'] = '123'
        app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
        app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_LENGTH'))*1024*1024
        app.run(debug=True)
        