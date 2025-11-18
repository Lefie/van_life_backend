from flask import Blueprint,jsonify
from .database import get_db
from bson import ObjectId
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity,jwt_required,JWTManager



metrics_routes_bp = Blueprint("metrics_routes", __name__)
db = get_db()
vans_collection = db["vans"]
saved_vans_collection = db["saved_vans"]
rentals_collection = db["rentals"]
views_collection = db["views"]
user_collection = db["users"]


@metrics_routes_bp.route("/api/metrics/activity", methods=["GET"])
def overall_stats():
    try:
        
        # count total 
        total_vans = vans_collection.count_documents({})
        total_saved = saved_vans_collection.count_documents({})
        total_rentals = rentals_collection.count_documents({})
        total_views = views_collection.count_documents({})
        total_users = user_collection.count_documents({})
        total_renters = user_collection.count_documents({"isHost":False})
        total_hosts = user_collection.count_documents({"isHost": True})

        avg_vans_per_host = round(total_vans / total_hosts, 1) if total_hosts > 0 else 0
        avg_bookings_per_van = round(total_rentals / total_vans) if total_vans > 0 else 0


        return jsonify(
            {"overall stats":{
            "total users": total_users,
            "total renters": total_renters,
            "total hosts": total_hosts,
            "total listings": total_vans,
            "total bookings": total_rentals,
            "total views": total_views,
            "total saves": total_saved},
            "engagement": {
                "average vans per host": avg_vans_per_host,
                "average bookings per van": avg_bookings_per_van
            }}), 200
    except Exception as e:
        print(e)
        return jsonify({"error":"Failed to calculate conversions"}), 500
        

@metrics_routes_bp.route("/api/metrics/host-performance")
@jwt_required()
def host_performance():
    try:
        host_id = get_jwt_identity()

        # hosts listings 
        van_listing_by_host = list(vans_collection.find({"hostId":host_id}))
        host_van_ids = [str(van["_id"]) for van in van_listing_by_host]

        if len(host_van_ids) == 0:
            return jsonify({"msg":"no listings yet"}), 200

        total_views_host = views_collection.count_documents({"van_id":{"$in": host_van_ids}})
        total_saves_host = saved_vans_collection.count_documents({"van_id":{"$in": host_van_ids}})
        total_bookings_host = rentals_collection.count_documents({"van_id": {"$in": host_van_ids}})


        van_booking_counts = []
        for van in van_listing_by_host:
            van_id = str(van["_id"])
            booking_count = rentals_collection.count_documents({"van_id":van_id})
            view_count = views_collection.count_documents({"van_id":van_id})
            save_count = saved_vans_collection.count_documents({"van_id":van_id})
        
            van_booking_counts.append({
                "van_id": van_id,
                "van_name":van["name"],
                "bookings":booking_count,
                "views":view_count,
                "saves": save_count
            })
        
        sorted_van_listings = sorted(van_booking_counts, key=lambda van:van["bookings"], reverse=True)
        top_listing = sorted_van_listings[0] if len(sorted_van_listings) > 0 else None



        return jsonify({
            "host_summary": {
                "total_listings": len(van_listing_by_host),
                "total_views": total_views_host,
                "total_saves": total_saves_host,
                "total_bookings": total_bookings_host
            },
            "top_listing": top_listing,
            "all_listings": van_booking_counts
        }), 200
    
    except Exception as e:
        return jsonify({"msg":"something went wrong"}), 500
    
@metrics_routes_bp.route("/api/metrics/popular-vans", methods=["GET"])
def popular_vans():
    try:
        # Aggregate bookings per van
        pipeline = [
            {
                "$group": {
                    "_id":"$van_id",
                    "booking_count": {"$sum":1}
                }
            },
            {"$sort": {"booking_count":-1}},
            {"$limit":10}
        ]
        top_booked = list(rentals_collection.aggregate(pipeline))
        
        top_van_list = []
        for van in top_booked:
            print(van)
            v = vans_collection.find_one({"_id":ObjectId(van["_id"])})
            if v:
                top_van_list.append({
                    "name":v["name"],
                    "type":v["type"],
                    "price":v["price"],
                    "booking":van["booking_count"]
                })
    

        # Most viewed vans
        view_pipeline = [
            {
                "$group": {
                    "_id": "$van_id",
                    "view_count": {"$sum": 1}
                }
            },
            {"$sort": {"view_count": -1}},
            {"$limit": 5}
        ]
        
        most_viewed = list(views_collection.aggregate(view_pipeline))
        most_viewed_list = []

        for van in most_viewed:
            v = vans_collection.find_one({"_id":ObjectId(van["_id"])})
            most_viewed_list.append({
                "name":v["name"],
                    "type":v["type"],
                    "price":v["price"],
                    "view":van["view_count"]
            })
        
        return jsonify({
            "most_booked": top_van_list,
            "most_viewed": most_viewed_list
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"error":"something went wrong"}), 500