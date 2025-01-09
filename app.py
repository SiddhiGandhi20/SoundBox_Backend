from flask import Flask, send_from_directory
from flask_pymongo import PyMongo
from config import Config
from flask_cors import CORS 
from routes.user_routes import create_auth_routes
from routes.login_routes import setup_login_routes
from routes.earphone_routes import create_earphones_routes
from routes.headphone_route import create_headphone_routes
from routes.smartwatch_routes import create_smartwatch_routes
from routes.earphones_details_routes import create_earphone_details_routes
from routes.headphone_details_routes import create_headphone_details_routes
from routes.smartwatch_details_routes import create_smartwatch_details_routes
from routes.adminlogin_routes import setup_admin_routes

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# Load MongoDB configuration
app.config.from_object(Config)
mongo = PyMongo(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

auth_bp = create_auth_routes(mongo.db)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(setup_login_routes(mongo.db))
app.register_blueprint(create_earphones_routes(mongo.db))
app.register_blueprint(create_headphone_routes(mongo.db))
app.register_blueprint(create_smartwatch_routes(mongo.db))
app.register_blueprint(create_earphone_details_routes(mongo.db, upload_folder="uploads"))
app.register_blueprint(create_headphone_details_routes(mongo.db, upload_folder="uploads"))
app.register_blueprint(create_smartwatch_details_routes(mongo.db, upload_folder="uploads"))
app.register_blueprint(setup_admin_routes(mongo.db))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)