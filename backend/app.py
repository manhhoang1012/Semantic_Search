

from flask import Flask, send_from_directory
from flask_cors import CORS  
import os

from backend.api.search_api import search_bp
from backend.api.crud_api import crud_bp

app = Flask(__name__)
import os

# Allow CORS for Vercel and local development
# In production, you might want to restrict this to your Vercel domain
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
if allowed_origins != "*":
    allowed_origins = allowed_origins.split(",")

CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

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