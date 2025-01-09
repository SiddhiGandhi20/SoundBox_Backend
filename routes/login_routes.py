import jwt
import datetime
from flask import Blueprint, request, jsonify
import re
from models.login_model import LoginModel

login_bp = Blueprint("login", __name__)

# Secret key for signing the token (this should be stored securely, e.g., in environment variables)
SECRET_KEY = "your_secret_key"

def setup_login_routes(db):
    login_model = LoginModel(db)

    @login_bp.route("/login", methods=["POST"])
    def user_login():
        """API endpoint for user login."""
        data = request.get_json()

        # Extract data
        email = data.get("email")
        password = data.get("password")

        # Input validation
        if not (email and password):
            return jsonify({"error": "Email and password are required"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email address"}), 400

        # Check credentials
        user = login_model.get_user_by_email(email)
        if not user or not login_model.check_password(user["password"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate token
        payload = {
            "id": str(user["_id"]),  # Assuming MongoDB ObjectId
            "email": user["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # Token expiry
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({"message": "Login successful", "token": token}), 200

    return login_bp
