from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from minio import Minio
import bcrypt
import os
import uuid
import threading
from datetime import datetime, timedelta
from time import sleep

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client['stack-overflow']
users = db['users']
files = db['files']
notifications = db['notifications']

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
    print('Creating a bucket...')
    minio_client.make_bucket(bucket_name)

print("MinIO connected successfully")

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
            notifications.insert_one({
                "username": user['username'],
                "message": f"New post by {username}",
                "timestamp": datetime.now(),
                "post_id": unique_id,
                "seen": False
            })

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
        try:
            with open(username_file, 'r') as file:
                current_user = file.read().strip()

            print("Fetching notifications for", current_user)

            # Fetch unread notifications from the notifications collection
            unread_notifications = list(notifications.find({
                "username": current_user
            }).sort("timestamp", -1))

            # Convert ObjectId to string for JSON serialization
            for notification in unread_notifications:
                notification["_id"] = str(notification["_id"])

            mark_notifications_seen()

            return jsonify({"notifications": unread_notifications}), 200
        except Exception as e:
            print("Something is wrong with the database,", e)
    return jsonify({"message": "User not signed in."}), 401

def mark_notifications_seen():
    """Mark all notifications as seen for the signed-in user."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        print("Marking notifications seen for", current_user)

        # Update all notifications for the current user as seen
        notifications.update_many(
            {"username": current_user},
            {"$set": {"seen": True}}
        )
        return jsonify({"message": "All notifications marked as seen."}), 200
    return jsonify({"message": "User not signed in."}), 401

@app.route('/notifications/unseen_count', methods=['GET'])
def get_unseen_notification_count():
    """Fetch the count of unseen notifications for the signed-in user."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        try:
            with open(username_file, 'r') as file:
                current_user = file.read().strip()

            # Fetch unseen notifications count
            unseen_count = notifications.count_documents({
                "username": current_user,
                "seen": False
            })
            return jsonify({"unseen_count": unseen_count}), 200
        except Exception as e:
            print("Something is wrong with the database,", e)
    return jsonify({"message": "User not signed in."}), 401

@app.route('/posts', methods=['GET'])
def get_posts():
    """Fetch all posts except the current user's in descending order of time, including file content."""
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        posts = files.find({"username": {"$ne": current_user}}).sort("timestamp", -1)

        post_list = []
        for post in posts:
            try:
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
                continue

        return jsonify({"posts": post_list}), 200
    return jsonify({"message": "User not signed in."}), 401

def cleanup_old_notifications():
    """Delete notifications older than 30 days."""
    while True:
        threshold_date = datetime.now() - timedelta(days=30)
        notifications.delete_many({"timestamp": {"$lt": threshold_date}})
        sleep(86400)  # Run daily

cleanup_thread = threading.Thread(target=cleanup_old_notifications, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
