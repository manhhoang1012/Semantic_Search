

from flask import Flask, send_from_directory
from flask_cors import CORS  
import os

from backend.api.search_api import search_bp
from backend.api.crud_api import crud_bp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

app.register_blueprint(search_bp, url_prefix="/api")
app.register_blueprint(crud_bp, url_prefix="/api")

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    # If the file exists in the frontend folder, serve it
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    # Otherwise fallback to index.html (useful for SPA routing if added later)
    return send_from_directory(FRONTEND_DIR, "index.html")

if __name__ == "__main__":
     app.run(debug=True)