from flask import Blueprint,Flask, request, jsonify
from flask_cors import CORS
from .database import get_db
from bson import ObjectId
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

db = get_db()

rental_routes_bp = Blueprint("rental_routes",__name__)
CORS(rental_routes_bp)
rentals_collection = db["rentals"]

@rental_routes_bp.route("/api/rentals/create_new_rental", methods=["POST"])
def create_new_rental():
    try:
        data = request.get_json()
        user_id = data["user_id"]
        start_date = data['startDate']
        end_date = data['endDate']
        
        start_date_list = start_date.split("-")
        start_date_details = [int(d) for d in start_date_list]
        start_date_obj = datetime(start_date_details[0],start_date_details[1],start_date_details[2])
        
        end_date_list = end_date.split("-")
        end_date_details = [int(d) for d in end_date_list]
        end_date_obj = datetime(end_date_details[0],end_date_details[1],end_date_details[2])

        doc = {
            "van_id":data["van_id"],
            "user_id":ObjectId(user_id),
            "start_date":start_date_obj,
            "end_date":end_date_obj,
            "created_at":datetime.now(ZoneInfo("America/New_York"))
        }

        rentals_collection.insert_one(doc)

        return jsonify({
            "msg":"rental booked!",
            "success":"true"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error":"error creating a new rental"}), 500


# get all rentals 
@rental_routes_bp.route("/api/rentals/get_all_rentals", methods=["GET"])
def get_all_rentals():
    try:
        all_rentals_cursor = rentals_collection.find({})
        all_rentals = []
        for rental in all_rentals_cursor:
            rental["_id"] = str(rental["_id"] )
            rental["user_id"] = str(rental["user_id"])
            all_rentals.append(rental)

        return jsonify({"rentals":all_rentals}), 200
    except Exception as e:
        print(e)
        return jsonify({"msg":"an error occured"}), 500