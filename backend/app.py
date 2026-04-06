

from flask import Flask
from flask_cors import CORS  

from backend.api.search_api import search_bp
from backend.api.crud_api import crud_bp

app = Flask(__name__)
CORS(app)   

app.register_blueprint(search_bp, url_prefix="/api")
app.register_blueprint(crud_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)