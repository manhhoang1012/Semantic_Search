# from flask import Flask
# from backend.api.search_api import search_bp
# from backend.api.crud_api import crud_bp

# app = Flask(__name__)

# app.register_blueprint(search_bp, url_prefix="/api")
# app.register_blueprint(crud_bp, url_prefix="/api")

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask
from flask_cors import CORS   # 👈 thêm dòng này

from backend.api.search_api import search_bp
from backend.api.crud_api import crud_bp

app = Flask(__name__)
CORS(app)   # 👈 thêm dòng này

app.register_blueprint(search_bp, url_prefix="/api")
app.register_blueprint(crud_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)