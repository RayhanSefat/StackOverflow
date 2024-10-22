from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import os

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client['user_database']
users = db['users']

# Define the file path for storing the username
USERNAME_FILE = 'username.txt'

@app.route('/', methods=['GET'])
def home():
    if os.path.exists(USERNAME_FILE):
        with open(USERNAME_FILE, 'r') as file:
            username = file.read().strip()
            return jsonify({"username": username}), 200
    return jsonify({"username": "Guest"}), 200

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Check if username already exists
    if users.find_one({"username": data['username']}):
        return jsonify({"message": "Username already exists"}), 409

    # Insert new user into the database
    users.insert_one({
        "username": data['username'],
        "password": hashed_password
    })
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    user = users.find_one({"username": data['username']})

    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        with open(USERNAME_FILE, 'w') as file:
            file.write(user['username'])
        return jsonify({"message": "Sign in successful"}), 200
    return jsonify({"message": "Invalid username or password"}), 401

@app.route('/signout', methods=['POST'])
def signout():
    if os.path.exists(USERNAME_FILE):
        os.remove(USERNAME_FILE)
    return jsonify({"message": "Signed out successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
