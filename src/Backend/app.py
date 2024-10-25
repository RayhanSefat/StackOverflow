from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from minio import Minio
import bcrypt
import os
import uuid
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client['stack-overflow']
users = db['users']
files = db['files']

# Initialize MinIO client
minio_client = Minio(
    os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    secure=False
)

# Ensure the bucket exists
bucket_name = "stack-overflow"
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

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
    """Handle saving the pasted content as a file on MinIO."""
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

        # Define file name
        unique_id = uuid.uuid4()
        file_name = f"{username}_file_{unique_id}.{extension}"

        # Save content to a temporary file
        temp_file_path = os.path.join('tmp', file_name)
        with open(temp_file_path, 'w') as file:
            file.write(content)

        # Upload file to MinIO
        minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=file_name,
            file_path=temp_file_path,
            content_type="text/plain"
        )

        # Clean up the local temporary file
        os.remove(temp_file_path)

        # Store the file path (URL) in MongoDB
        file_url = minio_client.presigned_get_object(bucket_name, file_name)
        db['files'].insert_one({
            "username": username,
            "filename": file_name,
            "file_url": file_url,
            "description": description,
            "timestamp": datetime.now()
        })

        return jsonify({"message": "File saved successfully.", "file_url": file_url}), 201

    except Exception as e:
        return jsonify({"message": "An unexpected error occurred.", "error": str(e)}), 500

@app.route('/notifications', methods=['GET'])
def get_notifications():
    """Fetch unread notifications for the signed-in user."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        user = users.find_one({"username": current_user})
        if user:
            return jsonify({"notifications": user.get('notifications', [])}), 200
    return jsonify({"message": "User not signed in."}), 401

@app.route('/notifications/mark_seen', methods=['POST'])
def mark_notifications_seen():
    """Mark all notifications as seen for the signed-in user."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        # Mark all notifications as seen for the current user
        users.update_one(
            {"username": current_user},
            {"$set": {"notifications.$[].seen": True}}
        )
        return jsonify({"message": "All notifications marked as seen."}), 200
    return jsonify({"message": "User not signed in."}), 401

@app.route('/notifications/unseen_count', methods=['GET'])
def get_unseen_notification_count():
    """Fetch the count of unseen notifications for the signed-in user."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        # Fetch unseen notifications count
        user = users.find_one({"username": current_user})
        if user:
            unseen_count = sum(1 for notification in user.get('notifications', []) if not notification.get('seen', False))
            return jsonify({"unseen_count": unseen_count}), 200
    return jsonify({"message": "User not signed in."}), 401

@app.route('/posts', methods=['GET'])
def get_posts():
    """Fetch all posts except the current user's in descending order of time."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        # Fetch all posts except the current user's, sorted by timestamp (descending order)
        posts = files.find({"username": {"$ne": current_user}}).sort("timestamp", -1)

        # Build the response, including file content from MinIO
        post_list = []
        for post in posts:
            post_list.append({
                "username": post['username'],
                "description": post['description'],
                "file_url": post['file_url'],
                "timestamp": post['timestamp']
            })

        return jsonify({"posts": post_list}), 200
    return jsonify({"message": "User not signed in."}), 401

if __name__ == '__main__':
    app.run(debug=True)
