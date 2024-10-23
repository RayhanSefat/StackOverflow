from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import os
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client['user_database']
users = db['users']
files = db['files']

# Define the directory for saving files
SAVE_FOLDER = 'saved_files'
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    """Get the username of the signed-in user."""
    username_file = f'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            username = file.read().strip()
            return jsonify({"username": username}), 200
    return jsonify({"username": "Guest"}), 200

@app.route('/signup', methods=['POST'])
def signup():
    """Handle user signup."""
    data = request.json
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    if users.find_one({"username": data['username']}):
        return jsonify({"message": "Username already exists"}), 409

    users.insert_one({
        "username": data['username'],
        "password": hashed_password
    })
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/signin', methods=['POST'])
def signin():
    """Handle user sign-in."""
    data = request.json
    user = users.find_one({"username": data['username']})

    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        with open('username.txt', 'w') as file:
            file.write(user['username'])
        return jsonify({"message": "Sign in successful"}), 200
    return jsonify({"message": "Invalid username or password"}), 401

@app.route('/signout', methods=['POST'])
def signout():
    """Handle user sign-out."""
    if os.path.exists('username.txt'):
        os.remove('username.txt')
    return jsonify({"message": "Signed out successfully"}), 200

@app.route('/save_content', methods=['POST'])
def save_content():
    """Handle saving the pasted content as a file."""
    try:
        data = request.json
        description = data.get('description')
        content = data.get('content')
        extension = data.get('extension')

        if not description or not content or not extension:
            return jsonify({"message": "Description, content, and extension are required."}), 400
        
        username = None
        if os.path.exists('username.txt'):
            with open('username.txt', 'r') as file:
                username = file.read().strip()

        if username is None:
            return jsonify({"message": "User not signed in."}), 401
        
        # Define the file name and path
        file_name = f"{username}_file.{extension}"
        file_path = os.path.join(SAVE_FOLDER, file_name)

        # Save the content to a file
        with open(file_path, 'w') as file:
            file.write(content)

        # Store file info in the database with timestamp
        db['files'].insert_one({
            "username": username,
            "filename": file_name,
            "filepath": file_path,
            "description": description,
            "timestamp": datetime.now()
        })

        return jsonify({"message": "File saved successfully.", "filename": file_name}), 201

    except Exception as e:
        return jsonify({"message": "An unexpected error occurred.", "error": str(e)}), 500

@app.route('/posts', methods=['GET'])
def get_posts():
    """Fetch all posts except the current user's in descending order of time."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        # Fetch all posts except the current user's, sorted by timestamp (descending order)
        posts = files.find({"username": {"$ne": current_user}}).sort("timestamp", -1)

        # Build the response, including file content
        post_list = []
        for post in posts:
            with open(post['filepath'], 'r') as content_file:
                file_content = content_file.read()
            post_list.append({
                "username": post['username'],
                "description": post['description'],
                "content": file_content,
                "timestamp": post['timestamp']
            })

        return jsonify({"posts": post_list}), 200
    return jsonify({"message": "User not signed in."}), 401

if __name__ == '__main__':
    app.run(debug=True)
