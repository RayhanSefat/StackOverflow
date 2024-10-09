from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import jwt
import datetime
import os
import logging

# Initialize Flask application
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure the secret key for JWT and logging
app.config['SECRET_KEY'] = 'Bangladesh 2.0'
logging.basicConfig(level=logging.DEBUG)

# Connect to MongoDB
try:
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))  # Use environment variable for MongoDB URI
    db = client['user_database']
    users = db['users']
    print('db is connected')
except Exception as e:
    logging.error("Error connecting to MongoDB: %s", e)

@app.route('/', methods=['GET'])
def home():
    token = request.headers.get('Authorization')
    logging.info(f"Received Token: {token}")

    if not token:
        return jsonify({"message": "Sign in first"}), 401
    
    try:
        token = token.replace('Bearer ', '')  # Strip the 'Bearer ' prefix
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']
        logging.info(f"Decoded user ID: {user_id}")

        user = users.find_one({"_id": user_id})
        if user:
            return jsonify({"message": f"Hello {user['username']}!"}), 200
        else:
            return jsonify({"message": "User not found!"}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired!"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token!"}), 403

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
        logging.error("Error occurred during signup: %s", e)
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
                logging.warning("Invalid password attempt for user: %s", data['username'])
                return jsonify({"message": "Invalid password"}), 401
        else:
            logging.warning("Invalid username attempt: %s", data['username'])
            return jsonify({"message": "Invalid username"}), 401
    except Exception as e:
        logging.error("Error occurred during signin: %s", e)
        return jsonify({"message": "An error occurred. Please try again later."}), 500

@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token is missing!"}), 403
    
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({"message": "Access granted!"}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired!"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token!"}), 403

if __name__ == '__main__':
    app.run(debug=True)
