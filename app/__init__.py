from flask import Flask
from flask_cors import CORS
from .database import get_db

def create_app():
    app = Flask(__name__)
    CORS(app)

    db = get_db()
    if db:
        app.mongo_db = db
        print(db)
        print("db initialized in app")
    

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def index():
        return 'Hi lemon'
    
    return app

__all__ = ["create_app"]