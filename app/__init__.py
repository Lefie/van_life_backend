from flask import Flask
from flask_cors import CORS
from .database import get_db
from .vans_routes import vans_routes_bp
from .users_routes import user_routes_bp

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    db = get_db()
    
    if db != None:
        app.mongo_db = db
        print(db)
        print("db initialized in app")
    
    app.register_blueprint(vans_routes_bp)
    app.register_blueprint(user_routes_bp)
    return app



