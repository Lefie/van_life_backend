from flask import Blueprint,Flask, request, jsonify
from flask_cors import CORS
from .database import get_db
from datetime import datetime
from bson import ObjectId
import uuid
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity,jwt_required,JWTManager


db = get_db()

user_routes_bp = Blueprint("users_routes", __name__)
CORS(user_routes_bp)
users_collection = db["users"]
auth_log_collection = db["auth_logs"]


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

        auth_log_collection.insert_one({
            "event":"login",
            "status":"success",
            "email":login_info["email"],
            "timestamp":datetime.utcnow()
        })

        return jsonify({
            "token":token,
            "user":logged_in_user,
            "loginSuccess":True}),200
    
    except Exception as e:
        print("error msg:",e)
        auth_log_collection.insert_one({
            "event":"login",
            "status":"failed",
            "email":login_info["email"],
            "timestamp":datetime.utcnow()
        })
        return jsonify({"error":"error logging in"}), 500


@user_routes_bp.route("/api/users/register", methods=["POST"])
def register():
    try:
        credential = request.get_json()
        usernameFound = users_collection.find_one({"name":credential["name"]})
        if usernameFound:
            return jsonify({"error":"username already exists"}), 409
        
        users_collection.insert_one(credential)
        auth_log_collection.insert_one({
            "event":"registration",
            "status":"success",
            "email":credential["email"],
            "user_type":"Renter" if credential["isHost"] == False else "Host",
            "timestamp":datetime.utcnow()
        })
        return jsonify({"msg":"you are in!"}), 201
    
    except Exception as e:
        print(e)
        auth_log_collection.insert_one({
            "event":"registration",
            "status":"failed",
            "email":credential["email"],
            "user_type":"Renter" if credential["isHost"] == False else "Host",
            "timestamp":datetime.utcnow()
        })
        return jsonify({"error":"error registering a new user"}), 500
    
@user_routes_bp.route("/api/users/<user_id>")
def get_user_info(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        user["_id"] = str(user["_id"])
        return jsonify({"user":user,
                        "msg":"success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"msg":"something went wrong"}), 500



@user_routes_bp.route("/api/users/auth-stats", methods=["GET"])
def auth_stats():
    try:
        jwt_protected_routes = [
        "/api/rentals",
        "/api/rentals/upcoming_rentals",
        "/api/rentals/rental_history",
        "/api/save/<van_id>",
        "/api/unsave/<van_id>",
        "/api/saved_vans",
        "/api/vans/host",
        "/api/vans/<van_id>/host",
        "/api/vans/van/host"
        ]

        total_logins = auth_log_collection.count_documents({"event":"login"})
        login_success = auth_log_collection.count_documents({"event":"login", "status":"success"})
        success_rate_login = -1 if total_logins == 0 else login_success / total_logins * 100

        total_registrations = auth_log_collection.count_documents({"event":"registration"})
        registration_success = auth_log_collection.count_documents({"event":"registration", "status":"success"})
        success_rate_registration = -1 if total_registrations == 0 else registration_success / total_registrations

        return jsonify({
            "total_logins":total_logins,
            "login_success":login_success,
            "login_success_rate":success_rate_login,
            "total_registrations":total_registrations,
            "registration_succes":registration_success,
            "registration_success_rate":success_rate_registration,
            "jwt_protected_endpoints":len(jwt_protected_routes),
            "protected_endpoints": jwt_protected_routes
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"error":"something went wrong"})

    
    

   