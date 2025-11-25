from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity,jwt_required,JWTManager
from datetime import timedelta
from .database import get_db
from .vans_routes import vans_routes_bp
from .users_routes import user_routes_bp
from .saved_vans_routes import saved_vans_routes_bp
from .rentals_routes import rental_routes_bp
from .metrics_routes import metrics_routes_bp
from .seed_data_routes import seed_data_route_bp
import os

def create_app():
    app = Flask(__name__)
    CORS(app, 
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        )
    secret_key = os.environ.get("JWT_SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    jwt = JWTManager(app)


    @app.route("/")
    def index():
        return "hello from flask"

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({
            'error': 'Missing token',
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({
            "error":"Invalid token"
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_loader(jwt_header, jwt_payload):
        return jsonify({
            "error":"Token expired"
        }), 401


    db = get_db()
    
    if db != None:
        app.mongo_db = db
        print(db)
        print("db initialized in app")
    
    app.register_blueprint(vans_routes_bp)
    app.register_blueprint(user_routes_bp)
    app.register_blueprint(saved_vans_routes_bp)
    app.register_blueprint(rental_routes_bp)
    app.register_blueprint(metrics_routes_bp)
    app.register_blueprint(seed_data_route_bp)
    
    return app



