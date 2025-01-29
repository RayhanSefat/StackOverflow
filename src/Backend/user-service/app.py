from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os
import bcrypt
from bson import ObjectId

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client['so-users']
users = db['users']

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

@app.route("/get_users_except_user/<username>", methods=['GET'])
def get_users_except_user(username):
    """Get all users except the user."""
    try:
        all_users = list(users.find({}, {"password": 0}))
        all_users_except_user = [user for user in all_users if user['username'] != username]
        usernames_of_the_remaining_users = [user['username'] for user in all_users_except_user]
        return jsonify({"users": usernames_of_the_remaining_users}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    default_directory = "F:/6th Semester/stack-overflow/public/"
    os.chdir(default_directory)
    
    app.run(port=5001)
