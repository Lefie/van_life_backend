
from flask import Blueprint,Flask, request, jsonify
from flask_cors import CORS
from .database import get_db
from bson import ObjectId
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, jwt_required

db = get_db()
vans_routes_bp = Blueprint("vans_routes", __name__)
CORS(vans_routes_bp)
van_collection = db["vans"]
user_collection = db["users"]
views_collection = db["views"]




@vans_routes_bp.route('/api/vans', methods=['GET'])
def all_vans():
    try:
        cursor = van_collection.find({})
        vans_list = []
        for van in cursor:
            van['_id'] = str(van['_id'])
            vans_list.append(van)
        return jsonify({"vans": vans_list}), 200
    except Exception as e:
        print(e)
        return jsonify({"error":"error fetching vans"}), 500

@vans_routes_bp.route('/api/vans/<van_id>')
def van_by_id(van_id):
    try:
        print("van by id: ",van_id)
        van = van_collection.find_one({'_id':ObjectId(van_id)})

        if not van:
            return jsonify({"error":"van not found"}),404
        
        views_collection.insert_one({
            "van_id":van_id,
            "viewed_at": datetime.utcnow()
        })
        
        van['_id'] = str(van['_id'])
        print(van)
        return jsonify({"van":van}), 200
    except Exception as e:
        print(e)
        return jsonify({"error":"error fetching van at id" + str(van_id)}), 500


# jwt required 
@vans_routes_bp.route("/api/vans/host")
@jwt_required()
def get_vans_by_host():
    host_id = get_jwt_identity()
    try:
        cursor  = van_collection.find({"hostId":host_id})
        vans_list = []
        for van in cursor:
            van['_id'] = str(van['_id'])
            vans_list.append(van)
        return jsonify({"vans": vans_list}), 200
    except Exception as e:
        print(e)
        return jsonify({"error":"error fetching vans at hostid 123"}), 500

# jwt required 
@vans_routes_bp.route('/api/vans/<van_id>/host', methods = ["GET","PUT", "DELETE"])
@jwt_required()
def van_by_id_host(van_id):
    method = request.method
    logged_in_host_id = get_jwt_identity()
    van = van_collection.find_one({
            "_id":ObjectId(van_id),
            "hostId":logged_in_host_id
    })
    if not van:
            return jsonify({"error":"van not found"}),404
    
    if van["hostId"]!= logged_in_host_id:
                return jsonify({"error":"host does not have access to this van"}), 403

    if method == "GET":
        try:
            van["_id"] = str(van["_id"])
            return jsonify({"van": van}), 200
        except Exception as e:
            print(e)
            return jsonify({"error":"error fetching van by id by host"}), 500
    elif method == "PUT":
        try:
            data_to_update = request.get_json()
            print("data to update", data_to_update)

            updated_res = van_collection.update_one({
                "_id":ObjectId(van_id),
                "hostId":logged_in_host_id
            }, {
                "$set": data_to_update
            } )
            print(updated_res)

            return jsonify({"data":"success"}), 200
        except Exception as e:
             print(e)
             return jsonify({"error":"error updating this van"}), 500
        
    elif method == "DELETE":
        try:
            deleted_res = van_collection.delete_one(
                { "_id":ObjectId(van_id),
                "hostId":logged_in_host_id})
            print(deleted_res)
            return jsonify({"delete_status":"success"}), 200
            
        except Exception as e:
            print(e)
            return jsonify({"error":"error deleting a van"}), 500


# jwt required 
# create a new van 
@vans_routes_bp.route('/api/vans/van/host', methods=["POST"])
@jwt_required()
def create_van_by_host():
    host_id = get_jwt_identity()
    try:
        print("create a new van",host_id)
        # make sure host is actually host
        data = request.get_json()
        data["hostId"] = host_id
        print(data)
        res = van_collection.insert_one(data)
        print("insertion res", res)
        data["_id"] = str(res.inserted_id)
        return jsonify({"van":data}), 200

    except Exception as e:
        print("error: ", e)
        return jsonify({"error":"error creating a new van by host"}), 500
 











