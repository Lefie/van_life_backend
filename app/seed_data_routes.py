from flask import Blueprint,Flask, request, jsonify
from flask_cors import CORS
from .database import get_db
from datetime import datetime
from bson import ObjectId
import uuid
import random
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity,jwt_required,JWTManager

db = get_db()

seed_data_route_bp = Blueprint("seed_data_routes", __name__)
CORS(seed_data_route_bp)

auth_logs_collection = db["auth_logs"]
rentals_collection = db["rentals"]
saved_vans_collection = db["saved_vans"]
user_collection = db["users"]
vans_collection = db["vans"]
views_collection = db["views"]

@seed_data_route_bp.route("/api/seed/users")
def get_users():
    try:
        num_of_users = user_collection.count_documents({})
        num_of_renters = user_collection.count_documents({"isHost":False})
        num_of_owners = user_collection.count_documents({"isHost":True})

        print(f""" 
            total users on the platform : {num_of_users}
            total users who are renters : {num_of_renters}
            total users who are owners  : {num_of_owners}
        """)

        return jsonify({
            "total_users": num_of_users,
            "total_renters": num_of_renters,
            "total_owners": num_of_owners
        }), 200
    
    except Exception as e:
        print(e)
        return jsonify({
           "msg":"something went wrong"
        }), 500

@seed_data_route_bp.route("/api/seed/users/<role>/<quant>", methods=["POST"])
def create_users(role, quant):
    try:
        roles = ["host", "renter"]
        
        if role not in roles:
            return jsonify({"msg":"role does not exist. either host or renter"}), 500
        
        if quant.isnumeric() == False:
            return jsonify({"msg":"quantity needs to be a number"}), 500

        names = [
            "Alex", "Jordan", "Morgan", "Casey", "Riley", "Avery", "Jamie", "Quinn",
            "Dakota", "River", "Sage", "Phoenix", "Taylor", "Blake", "Drew", "Cameron",
            "Parker", "Skyler", "Sam", "Charlie", "Dakota", "Elliott", "Finley", "Harley",
            "Jessie", "Kerry", "Leslie", "Marley", "Oakley", "Reese", "Rowan", "Sawyer",
            "Shiloh", "Sidney", "Skylar", "Spencer", "Sutton", "Teagan", "Zephyr"
        ]

        quant = int(quant)

        new_users_list = []

        for i in range(quant):
            username = random.choice(names)
            #username = "lemon"
            user = user_collection.find_one({"name":username})
        
            if user != None:
                username = user["name"]

                while user != None:
                    digit = random.randint(0,9)
                    username +=str(digit)
                    user = user_collection.find_one({"name":username})            

            email = username.lower() +"@gmail.com"
            password = "123"
            isHost = True if role == "host" else False
            seed_user_data = {
                "name": username, 
                "email":email,
                "password":password,
                "isHost":isHost
            }
            new_users_list.append(seed_user_data)
        
        print(new_users_list)
    
        user_collection.insert_many(new_users_list)


        return jsonify({"msg":"success"}), 200
    
    except Exception as e:
        print(e)
        return jsonify({"msg": "something went wrong"}), 500

@seed_data_route_bp.route("/api/seed/vans/<quant>", methods=["POST"])
def create_vans(quant):
    hosts = list(user_collection.find({"isHost":True}))
    if quant.isnumeric() == False:
        return jsonify({"msg":"quant must be a number"}), 500

    quant = int(quant)
    
    try:
        def create_name():

            first_words = [
                "Beach",
                "Mountain",
                "Desert",
                "Forest",
                "Sunset",
                "Midnight",
                "Silver",
                "Golden",
                "Wandering",
                "Nomad",
                "Wild",
                "Rustic",
                "Modern",
                "Classic",
                "Swift",
                "Dreamy",
                "Starry",
                "Happy",
                "Free",
                "Lucky",
                "Bold",
                "Mighty",
                "Gentle",
                "Cozy",
                "Sleek",
                "Rugged",
                "Smooth",
                "Endless",
                "Open",
                "High",
                "Blue",
                "Green",
                "Red",
                "Spirit",
                "Soul",
                "Heart",
                "Echo",
                "Thunder",
                "Ocean",
                "Cloud",
            ]

            second_words = [
                "Rider",
                "Explorer",
                "Wanderer",
                "Seeker",
                "Traveler",
                "Nomad",
                "Adventurer",
                "Dreamer",
                "Voyager",
                "Scout",
                "Hunter",
                "Charger",
                "Runner",
                "Roamer",
                "Cruiser",
                "Drifter",
                "Pioneer",
                "Ranger",
                "Tracker",
                "Soul",
                "Spirit",
                "Breeze",
                "Wave",
                "Horizon",
                "Journey",
                "Quest",
                "Path",
                "Trail",
                "Road",
                "Compass",
                "Eagle",
                "Wolf",
                "Bear",
                "Phoenix",
                "Dragon",
                "Star",
                "Moon",
                "Sun",
                "Fire",
                "Storm",
            ]
    
            van_name = random.choice(first_words) + " " + random.choice(second_words)
            # Mercury Explorer_5
            #van_name = "Mercury Explorer"
            print(van_name)
            van = vans_collection.find_one({"name":van_name})
            if van != None:
                van_name += "_"
                while van != None:
                    van_name += str(random.randint(0,9))
                    van = vans_collection.find_one({"name":van_name})
            
            return van_name

        def create_description(name):
            # Generic van descriptions - use [van_name] as placeholder
            van_descriptions = [
                "[van_name] is a van that was made for travelling. The inside is comfortable and cozy, with plenty of space to stretch out in. There's a small kitchen, so you can cook if you need to. You'll feel like home as soon as you step out of it.",
                
                "[van_name] offers a luxurious travel experience with premium furnishings and modern amenities. Every detail has been carefully designed for maximum comfort and convenience on the road.",
                
                "[van_name] is your cozy home on wheels. Equipped with a full kitchen, comfortable sleeping area, and plenty of storage, it's the perfect van for extended road trips and adventures.",
                
                "With this van, you can take your travel life to the next level. [van_name] is a sustainable vehicle that's perfect for people who are looking for a stylish, eco-friendly mode of transport that can go anywhere.",
                
                "[van_name] combines sustainability with style. Built with eco-conscious materials and efficient systems, it's the perfect choice for travelers who care about the environment.",
                
                "Travel responsibly with [van_name]. This van features solar panels, a composting toilet, and water-efficient systems, making it an environmentally-friendly choice for conscious adventurers.",
                
                
                "[van_name] is a van inspired by surfers and travelers. It was created to be a portable home away from home, but with some cool features in it you won't find in an ordinary camper.",
                
                "[van_name] is built for adventure seekers and outdoor enthusiasts. With rugged suspension, all-terrain capabilities, and outdoor gear storage, you're ready to explore anywhere.",
                
                "[van_name] embodies the spirit of freedom and exploration. Whether you're hitting the beach, mountains, or desert, this van is your trusted companion for unforgettable journeys.",
                
      
                "[van_name] proves that you don't need much to live well. This minimalist van offers smart storage solutions and clean modern design in a compact, efficient package.",
                
                "Experience van life in its purest form with [van_name]. Stripped-down essentials with thoughtful design—perfect for travelers who value simplicity and freedom.",
                
                
                "[van_name] is perfect for families and groups. Spacious enough for multiple travelers, it features a functional kitchen, comfortable sleeping arrangements, and entertainment options for everyone.",
                
                "Create lasting memories with [van_name]. This family-friendly van has plenty of room for everyone, a well-equipped kitchen, and comfortable amenities for group adventures.",
                
              
                "[van_name] proves that budget-friendly travel doesn't mean sacrificing comfort. This reliable van offers great value with all the essentials you need for an amazing trip.",
                
                "Travel on a budget without compromising on experience. [van_name] is affordable, reliable, and packed with practical features for smart travelers.",
                
              
                "[van_name] is built tough for the toughest roads. With reinforced suspension, high clearance, and durable construction, it's ready to take you off the beaten path.",
                
                "Conquer any terrain with [van_name]. This rugged vehicle is designed for serious adventurers who want to explore remote locations and challenging landscapes.",
                
                
                "[van_name] redefines van life luxury. Premium fixtures, gourmet kitchen setup, quality bedding, and high-end entertainment systems make this a 5-star mobile experience.",
                
                "Enjoy the finer things while traveling with [van_name]. This luxury van features premium finishes, modern tech, and sophisticated amenities that rival hotel accommodations.",
                
          
                "[van_name] is the perfect escape for couples looking to reconnect with nature and each other. Intimate yet comfortable, it's your private retreat on the road.",
                
                "Plan the perfect romantic getaway in [van_name]. Cozy sleeping quarters, intimate dining space, and stunning travel destinations await.",
                
               
                "[van_name] is ideal for solo travelers seeking independence and adventure. Compact yet fully equipped, it gives you complete freedom to explore at your own pace.",
                
                "Take control of your journey with [van_name]. Perfect for solo adventurers, this van offers all the independence and comfort you need to explore the world.",
            ]
            descritpion = random.choice(van_descriptions)
            descritpion = descritpion.replace("[van_name]", name)
            return descritpion
        
        def get_image():
            img_url_list = ["https://images.unsplash.com/photo-1561361513-2d000a50f0dc?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8dmFufGVufDB8fDB8fHww",
                            "https://images.squarespace-cdn.com/content/v1/5adbc31350a54fda2d547576/1709243385350-6RJCU8IPO0723LSF93NZ/0-Claus-Boho-Camper-Vans.jpg",
                            "https://robbreport.com/wp-content/uploads/2023/12/boho01.jpg?w=800","https://images.stockcake.com/public/3/0/a/30afc7cf-70bf-47ac-bd66-c96d2d0a682b_large/beachside-bohemian-van-stockcake.jpg",
                            "https://www.theinertia.com/wp-content/uploads/2020/05/Campervans.jpg",
                            "https://escapecampervans.com/wp-content/uploads/2020/02/Escape-Camper-Vans-RB25-13.webp",
                            "https://res.cloudinary.com/outdoorsy/image/upload/a_exif,q_auto,f_auto,w_auto,h_1080,w_1920,c_fill/v1704764302/p/rentals/395581/images/jrkpnrtflehdmypahfnr.jpg",
                            "https://vandoit.com/wp-content/uploads/2023/06/41087-15-of-31.jpg",
                            "https://vandoit.com/wp-content/uploads/2023/11/41505-7-of-32-1.jpg",
                            "https://vandoit.com/wp-content/uploads/2023/05/41094-10-of-31-1024x683.jpg",
                            "https://i.pinimg.com/474x/d3/a3/0b/d3a30b142bc8eb40e1142697000b30f7.jpg",
                            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRz4K8kILad9Fcd1Xsv_z98Xcvopqsql4QNYg&s",
                            "https://i.pinimg.com/236x/63/1d/5f/631d5f17c57a2fe0cf6ebd8ac0a05c0c.jpg",
                            "https://images.pexels.com/photos/32036002/pexels-photo-32036002/free-photo-of-vintage-yellow-camper-van-in-scenic-park.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"]
            return random.choice(img_url_list)
        new_van_list = []
        for i in range(quant):
            van_name = create_name()
            van_description = create_description(van_name)
            van_price = random.randint(45, 250)
            van_img_url = get_image()
            van_type = random.choice(["rugged","luxury","simple"])
            host = random.choice(hosts)
            van_host_id = str(host["_id"])

            new_van_data = {
                "name":van_name,
                "price":van_price,
                "description": van_description,
                "imageUrl":van_img_url,
                "type":van_type,
                "hostId": van_host_id
            }

            new_van_list.append(new_van_data)
        
        vans_collection.insert_many(new_van_list)
        
        
        return jsonify({"msg":"vans added"}), 200
        
    except Exception as e:
        print(e)
        return jsonify({"msg":"something went wrong"}), 500