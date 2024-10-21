from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
import bcrypt
import jwt
import datetime
from werkzeug.utils import secure_filename
from functools import wraps
import logging

# Initialize Flask application
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure app secret key, file upload folder, and allowed file extensions
app.config['SECRET_KEY'] = 'Bangladesh 2.0'
app.config['UPLOAD_FOLDER'] = './uploads'  # Folder to save files (optional)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB
ALLOWED_EXTENSIONS = {'c', 'cpp', 'java', 'py', 'js'}  # Allowed file extensions

# Initialize logging
logging.basicConfig(level=logging.WARNING)

# Connect to MongoDB
try:
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))  # Use environment variable for MongoDB URI
    db = client['user_database']
    users = db['users']
    posts = db['posts']  # Collection to store posts with files
    logging.info('MongoDB connected successfully')
except Exception as e:
    logging.error("Error connecting to MongoDB: %s", e)

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# JWT token verification decorator
def verify_token_required(f):
    @wraps(f)  # This ensures the original function's name is retained
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Sign in first"}), 401
        
        try:
            token = token.replace('Bearer ', '')  # Strip the 'Bearer ' prefix
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user_id = decoded['user_id']  # Attach user_id to request object
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 403
        return f(*args, **kwargs)
    return wrapper  # Return the wrapped function

@app.route('/', methods=['GET'])
@verify_token_required
def home():
    try:
        user = users.find_one({"_id": request.user_id})
        if user:
            return jsonify({"message": f"Hello {user['username']}!"}), 200
        else:
            return jsonify({"message": "User not found!"}), 404
    except Exception as e:
        logging.error(f"Error fetching the user: {str(e)}")
        return jsonify({"message": "An error occurred."}), 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        users.insert_one({
            "first_name": data['fname'],
            "last_name": data['lname'],
            "email": data['email'],
            "username": data['username'],
            "password": hashed_password  # Store hashed password
        })
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        logging.error(f"Error occurred during signup: {str(e)}")
        return jsonify({"message": "An error occurred. Please try again later."}), 500

@app.route('/signin', methods=['POST'])
def signin():
    try:
        data = request.json
        user = users.find_one({"username": data['username']})

        if user:
            stored_password = user['password']

            if bcrypt.checkpw(data['password'].encode('utf-8'), stored_password):
                # Create JWT token
                token = jwt.encode({
                    'user_id': str(user['_id']),
                    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)  # Token expires in 1 hour
                }, app.config['SECRET_KEY'], algorithm='HS256')

                return jsonify({'token': token}), 200
            else:
                logging.warning(f"Invalid password attempt for user: {data['username']}")
                return jsonify({"message": "Invalid password"}), 401
        else:
            logging.warning(f"Invalid username attempt: {data['username']}")
            return jsonify({"message": "Invalid username"}), 401
    except Exception as e:
        logging.error(f"Error occurred during signin: {str(e)}")
        return jsonify({"message": "An error occurred. Please try again later."}), 500

@app.route('/upload', methods=['POST'])
@verify_token_required
def upload():
    try:
        # Get the user details using the user_id from the token
        user = users.find_one({"_id": request.user_id})
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Check if the post content is included in the request
        post_content = request.form.get('content')

        if not post_content:
            return jsonify({"message": "Post content is missing"}), 400

        # Check if a file is part of the request
        if 'file' not in request.files:
            return jsonify({"message": "No file part in the request"}), 400
        
        file = request.files['file']

        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400

        # Check if file is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Save the file to the uploads folder
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Insert post with file content into MongoDB
            posts.insert_one({
                "username": user['username'],
                "content": post_content,
                "filename": filename,
                "filepath": filepath,  # Store the file path instead of binary data
            })

            return jsonify({"message": "File uploaded successfully"}), 201
        else:
            return jsonify({"message": "Invalid file type"}), 400
    except Exception as e:
        logging.error(f"Error occurred while uploading the file: {str(e)}")
        return jsonify({"message": "Error occurred while uploading the file"}), 500

if __name__ == '__main__':
    # Ensure the uploads folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(debug=True)
