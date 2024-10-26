from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from minio import Minio
import bcrypt
import os
import uuid
import threading
from datetime import datetime, timedelta, time

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
        uid_str = uuid.uuid4().urn
        unique_id = uid_str[9:]
        file_name = f"{username}_file_{unique_id}.{extension}"

        # Save content to a temporary file
        temp_file_path = os.path.join('tmp', file_name)
        with open(temp_file_path, 'w') as file:
            file.write(content)

        # Upload file to MinIO without making it public
        minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=file_name,
            file_path=temp_file_path,
            content_type="text/plain"
        )

        # Clean up the local temporary file
        os.remove(temp_file_path)

        # Store the file name (not URL) in MongoDB for security
        db['files'].insert_one({
            "post_id": unique_id,
            "username": username,
            "filename": file_name,
            "description": description,
            "timestamp": datetime.now()
        })

        # Add notification for other users
        users_to_notify = users.find({"username": {"$ne": username}})
        for user in users_to_notify:
            users.update_one(
                {"username": user['username']},
                {"$push": {"notifications": {
                    "message": f"New post by {username}: {description}",
                    "timestamp": datetime.now(),
                    "post_id": unique_id,
                    "seen": False
                }}}
            )

        return jsonify({"message": "File saved successfully."}), 201

    except Exception as e:
        return jsonify({"message": "An unexpected error occurred.", "error": str(e)}), 500

@app.route('/post/<post_id>', methods=['GET'])
def get_post(post_id):
    """Retrieve a post by its post_id."""
    try:
        # Find the file metadata in MongoDB
        post = db['files'].find_one({"post_id": post_id})

        if not post:
            return jsonify({"message": "Post not found."}), 404

        # Retrieve file name and description from MongoDB
        file_name = post['filename']
        description = post['description']
        username = post['username']
        timestamp = post['timestamp']

        # Download file content from MinIO to a temporary location
        temp_file_path = os.path.join('tmp', file_name)
        minio_client.fget_object(
            bucket_name=bucket_name,
            object_name=file_name,
            file_path=temp_file_path
        )

        # Read the content from the downloaded file
        with open(temp_file_path, 'r') as file:
            content = file.read()

        # Clean up the temporary file after reading
        os.remove(temp_file_path)

        # Prepare response data
        response_data = {
            "post_id": post_id,
            "username": username,
            "description": description,
            "content": content,
            "timestamp": timestamp
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the post.", "error": str(e)}), 500

@app.route('/notifications', methods=['GET'])
def get_notifications():
    """Fetch unread notifications for the signed-in user."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        mark_notifications_seen()

        user = users.find_one({"username": current_user})
        notifications = user.get('notifications')
        notifications = notifications[::-1]
        if user:
            return jsonify({"notifications": notifications}), 200
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
    """Fetch all posts except the current user's in descending order of time, including file content."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        # Fetch all posts except the current user's, sorted by timestamp (descending order)
        posts = files.find({"username": {"$ne": current_user}}).sort("timestamp", -1)

        # Build the response, including file content from MinIO
        post_list = []
        for post in posts:
            try:
                # Retrieve the file content from MinIO
                file_data = minio_client.get_object(bucket_name, post['filename'])
                content = file_data.read().decode("utf-8")
                file_data.close()

                post_list.append({
                    "username": post['username'],
                    "description": post['description'],
                    "content": content,  # Include the file content
                    "timestamp": post['timestamp']
                })
            except Exception as e:
                # If there is an error reading the file, skip this post
                continue

        return jsonify({"posts": post_list}), 200
    return jsonify({"message": "User not signed in."}), 401

@app.route('/fetch_file/<filename>', methods=['GET'])
def fetch_file(filename):
    """Allow the owner to view their own file content securely."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        # Fetch the file document
        file_doc = files.find_one({"filename": filename, "username": current_user})
        if not file_doc:
            return jsonify({"message": "File not found or access denied."}), 404

        # Retrieve the file content from MinIO
        try:
            file_data = minio_client.get_object(bucket_name, filename)
            content = file_data.read().decode("utf-8")
            file_data.close()
        except Exception as e:
            return jsonify({"message": "Could not retrieve file.", "error": str(e)}), 500

        return jsonify({"content": content, "description": file_doc['description']}), 200

    return jsonify({"message": "User not signed in."}), 401

def cleanup_old_notifications():
    """Delete notifications older than 30 days for all users."""
    while True:
        # Define the threshold date
        threshold_date = datetime.now() - timedelta(days=30)
        
        # Update each user by removing notifications older than 30 days
        users.update_many(
            {},
            {"$pull": {"notifications": {"timestamp": {"$lt": threshold_date}}}}
        )
        
        # Sleep for 24 hours before running the next cleanup
        time.sleep(86400)  # 86400 seconds = 24 hours

# Start the cleanup job in a separate thread
cleanup_thread = threading.Thread(target=cleanup_old_notifications, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
