
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
        van = van_collection.find_one({'id':van_id})

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
    
@vans_routes_bp.route('/api/host/<host_id>/vans/<van_id>')
def van_by_id_host(host_id, van_id):
    try:
        van = van_collection.find_one({"id":van_id})
        if van["hostId"]!= host_id:
            return jsonify({"error":"host does not have access to this van"}), 403
        if not van:
            return jsonify({"error":"van not found"}),404
        van["_id"] = str(van["_id"])
        return jsonify({"van": van})
    except Exception as e:
        print(e)
        return jsonify({"error":"error fetching van by id by host"}), 500












