from flask import Blueprint,Flask, request, jsonify
from flask_cors import CORS
from .database import get_db
from bson import ObjectId

db = get_db()

user_routes_bp = Blueprint("users_routes", __name__)
CORS(user_routes_bp)
users_collection = db["users"]


@user_routes_bp.route('/api/users/login', methods=["POST"])
def login():
    try:
        login_info = request.get_json()
        foundUser = users_collection.find_one({"email":login_info["email"]})
        if not foundUser:
            return jsonify({"error":"user cannot be found"}), 404
        
        if foundUser["password"] != login_info["password"]:
            return jsonify({"error":"user password incorrect"}), 401

    
        return jsonify({
            "loginSuccess":True, 
            "token":"Have a nice day!"})
    except Exception as e:
        print(e)
        return jsonify({"error":"error logging in"}), 500

