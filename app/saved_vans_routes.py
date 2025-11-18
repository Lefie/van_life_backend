from flask import Blueprint,Flask, request, jsonify
from flask_cors import CORS
from .database import get_db
from bson import ObjectId
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity,jwt_required,JWTManager


db = get_db()

saved_vans_routes_bp = Blueprint("saved_vans_routes", __name__)
CORS(saved_vans_routes_bp)
saved_vans_collections = db["saved_vans"]

@saved_vans_routes_bp.route("/api/save/<van_id>", methods=["POST"])
@jwt_required()
def save_van(van_id):
    try:
        loggedin_user_id = get_jwt_identity()
        doc = {
            "van_id":van_id,
            "user_id":loggedin_user_id,
            "saved_at":datetime.now(ZoneInfo("America/New_York"))
        }       

        existing_save = saved_vans_collections.find({"van_id":van_id, 
                                                     "user_id":loggedin_user_id})
    
        results = len(list(existing_save))
        
        if results != 0:
            return jsonify({
                "success": "false",
                "msg":"van already saved"}), 400


        saved_vans_collections.insert_one(doc)

        return jsonify({
            "success":"true",
            "msg":"saved!"}),200
    
    except Exception as e:
        print(e)
        return jsonify({"error":"an error occurred when saving van"}), 500




@saved_vans_routes_bp.route("/api/unsave/<van_id>", methods=["DELETE"])
@jwt_required()
def unsave(van_id):
    loggedin_user_id = get_jwt_identity()
    print(loggedin_user_id, " form unsave api")
    try:
       # find one to make sure that it exists 
       doc = saved_vans_collections.find_one_and_delete({"user_id":loggedin_user_id,"van_id":van_id})
       doc["_id"] = str(doc["_id"])
    
       return jsonify({"success":"true",
                       "deleted_doc":doc}), 200

    except Exception as e:
        print(e)
        return jsonify({"error":"an error occurred"}), 500
    

@saved_vans_routes_bp.route("/api/get_saved_vans", methods=["GET"])
def get_saved_rentals():
    try:
        saved_vans = saved_vans_collections.find({})
        saved_vans_list = []
        for van in saved_vans:
            van["_id"] = str(van["_id"])
            saved_vans_list.append(van)

        return jsonify({"saved_vans":saved_vans_list, "msg":"retrieval complete!"}),200
    except Exception as e:
        print(e)
        return jsonify({"error":"an error occured retrieving all saved vans"}), 500
    
@saved_vans_routes_bp.route("/api/saved_vans", methods=["GET"])
@jwt_required()
def get_saved_vans_by_user_id():
    try:
        loggedin_user_id = get_jwt_identity()
        print(loggedin_user_id)
        saved_vans = saved_vans_collections.find({"user_id":loggedin_user_id})
        saved_vans_list = []
        for van in saved_vans:
            van["_id"] = str(van["_id"])
            saved_vans_list.append(van)

        return jsonify({
            "success":"true",
            "saved_vans":saved_vans_list
            }), 200
    except Exception as e:
        print(e)
        return jsonify({"error":"an error occurred getting vans by user"}), 500