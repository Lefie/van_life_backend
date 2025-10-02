
from flask import Blueprint,Flask, request, jsonify
from flask_cors import CORS
from .database import get_db
from .data import get_vans_data, get_user_data
from bson import ObjectId

db = get_db()
vans_routes_bp = Blueprint("vans_routes", __name__)
CORS(vans_routes_bp)
van_collection = db["vans"]
user_collection = db["users"]


# set up pre-existing data 
"""
van_data = get_vans_data()
for van in van_data:
    van_collection.insert_one(van)

user_data = get_user_data()
users_collection.insert_one(user_data)
"""

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
        
        van['_id'] = str(van['_id'])
        print(van)
        return jsonify({"van":van}), 200
    except Exception as e:
        print(e)
        return jsonify({"error":"error fetching van at id" + str(van_id)}), 500

@vans_routes_bp.route('/api/host/<host_id>/vans')
def vans_by_host(host_id):
    print(host_id)
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

# to replace the api above 
@vans_routes_bp.route("/api/vans/host/<host_id>")
def get_vans_by_host(host_id):
    print(host_id)
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


@vans_routes_bp.route('/api/vans/<van_id>/host/<host_id>', methods = ["GET","PUT", "DELETE"])
def van_by_id_host(host_id, van_id):
    method = request.method

    van = van_collection.find_one({
            "_id":ObjectId(van_id),
            "hostId":host_id
    })
    if not van:
                return jsonify({"error":"van not found"}),404
    
    if van["hostId"]!= host_id:
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
                "hostId":host_id
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
                "hostId":host_id})
            print(deleted_res)
            return jsonify({"delete_status":"success"}), 200
            
        except Exception as e:
            print(e)
            return jsonify({"error":"error deleting a van"}), 500



# create a new van 
@vans_routes_bp.route('/api/vans/van/host/<host_id>', methods=["POST"])
def create_van_by_host(host_id):
    try:
        print("create a new van",host_id)
        # make sure host is actually host
        data = request.get_json()
        print(data)
        res = van_collection.insert_one(data)
        print("insertion res", res)
        data["_id"] = str(res.inserted_id)
        return jsonify({"van":data}), 200

    except Exception as e:
        print("error: ", e)
        return jsonify({"error":"error creating a new van by host"}), 500
 











