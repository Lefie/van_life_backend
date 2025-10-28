from flask import Blueprint,Flask, request, jsonify
from flask_cors import CORS
from .database import get_db
from bson import ObjectId
import uuid
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity,jwt_required,JWTManager


db = get_db()

user_routes_bp = Blueprint("users_routes", __name__)
CORS(user_routes_bp)
users_collection = db["users"]


@user_routes_bp.route('/api/users/login', methods=["POST"])
def login():
    try:
        login_info = request.get_json()
        print("login",login_info)
        foundUser = users_collection.find_one({"email":login_info["email"]})
        if not foundUser:
            return jsonify({"error":"user cannot be found"}), 404
        
        if foundUser["password"] != login_info["password"]:
            return jsonify({"error":"user password incorrect"}), 401

        foundUserId = str(foundUser["_id"])
        foundUser["_id"] = str(foundUser["_id"])
        logged_in_user = foundUser
        logged_in_user["password"] = None
        print(logged_in_user)
        token = create_access_token(foundUserId)

        return jsonify({
            "token":token,
            "user":logged_in_user,
            "loginSuccess":True}),200
    
    except Exception as e:
        print("error msg:",e)
        return jsonify({"error":"error logging in"}), 500


@user_routes_bp.route("/api/users/register", methods=["POST"])
def register():
    try:
        credential = request.get_json()
        usernameFound = users_collection.find_one({"name":credential["name"]})
        if usernameFound:
            return jsonify({"error":"username already exists"}), 409
        
        users_collection.insert_one(credential)
        return jsonify({"msg":"you are in!"}), 201
    
    except Exception as e:
        print(e)
        return jsonify({"error":"error registering a new user"}), 500
    