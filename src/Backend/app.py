from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import os

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})  

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))  # Use environment variable for MongoDB URI
db = client['user_database']  
users = db['users']  

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the backend API!"})

@app.route('/signup', methods=['POST'])
def signup():
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

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    user = users.find_one({"username": data['username']})
    
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        return jsonify({"message": "Sign-in successful"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

if __name__ == '__main__':
    app.run(debug=True)
