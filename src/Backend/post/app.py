from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os
from minio import Minio
import uuid
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client['so-posts']
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
    print('Creating a bucket...')
    minio_client.make_bucket(bucket_name)
print("MinIO connected successfully")

@app.route('/', methods=['GET'])
def home():
    """Get the username of the signed-in user."""
    print("Checking for the file...")
    username_file = f'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            username = file.read().strip()
            return jsonify({"username": username}), 200
    return jsonify({"username": "Guest"}), 200

@app.route('/save_content', methods=['POST'])
def save_content():
    """Handle saving the pasted content as a file on MinIO."""
    try:
        data = request.json
        description = data.get('description')
        content = data.get('content')
        extension = data.get('extension')

        # print(description)
        # print(content)
        # print(extension)

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
        
        # print("User is signed in")

        # print(os.path)

        # Save content to a temporary file
        temp_file_path = os.path.join('', file_name)
        print(temp_file_path)
        with open(temp_file_path, 'w') as file:
            file.write(content)

        print("Saving to minio")

        # Upload file to MinIO without making it public
        minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=file_name,
            file_path=temp_file_path,
            content_type="text/plain"
        )

        print("Saved to minio")

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
        users_to_notify = []
        response = requests.get("http://localhost:5001/get_users_except_user/" + username)
        print(response.json())
        if response.status_code == 200:
            users_to_notify = response.json().get("users", [])
            # print("Users to notify:", users_to_notify)
        for user in users_to_notify:
            requests.post("http://localhost:5003/notifications/add", json={
                "username": user,
                "message": f"New post by {username}",
                "post_id": unique_id
            })

        return jsonify({"message": "File saved successfully."}), 201

    except Exception as e:
        print(e)
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

@app.route('/posts', methods=['GET'])
def get_posts():
    """Fetch all posts except the current user's in descending order of time, including file content."""
    # print("Checking for the file...")
    username_file = 'username.txt'

    try:
        if os.path.exists(username_file):
            # print("File found")
            with open(username_file, 'r') as file:
                current_user = file.read().strip()
            
            print(current_user, "is the current user")

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
                    print("The exception is:", e)
                    continue

            return jsonify({"posts": post_list}), 200
    except Exception as e:
        print(e)
    print( "File not found")
    return jsonify({"message": "User not signed in."}), 401

if __name__ == '__main__':
    default_directory = "F:/6th Semester/stack-overflow/public/"
    os.chdir(default_directory)

    app.run(port=5002)
