from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timedelta
from time import sleep
import os
import threading

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client['so-notifications']
notifications = db['notifications']

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

@app.route('/notifications/add', methods=['POST'])
def add_notification():
    """Add a new notification for the signed-in user."""
    data = request.json
    username_file = 'username.txt'
    if os.path.exists(username_file):
        with open(username_file, 'r') as file:
            current_user = file.read().strip()

        data["timestamp"] = datetime.now()
        data["seen"] = False

        notifications.insert_one(data)
        return jsonify({"message": "Notification added successfully."}), 201
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
    default_directory = "F:/6th Semester/stack-overflow/public/"
    os.chdir(default_directory)

    app.run(port=5003)
