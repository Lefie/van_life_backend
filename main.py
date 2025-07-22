import os
from app import create_app
from flask import Flask

# app = create_app()
app = Flask(__name__)

# simple test
@app.route("/")
def index():
    return "hello from flask"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)