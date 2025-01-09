from flask import Blueprint, request, jsonify
import re
from models.user_model import UserModel

# Blueprint setup
auth_bp = Blueprint("auth", __name__)

def create_auth_routes(db):
    user_model = UserModel(db)

    @auth_bp.route("/user-signup", methods=["POST"])
    def signup():
        """API endpoint to register a new user."""
        data = request.get_json()

        # Check if data was successfully decoded
        if not data:
            return jsonify({"error": "Invalid JSON format"}), 400

        # Log received data
        print(f"Received data: {data}")

        # Extract data from request
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        # Input validation
        if not (name and email and password and confirm_password):
            return jsonify({"error": "All fields are required"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email address"}), 400

        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400

        # Check for duplicate email and mobile
        if user_model.is_email_registered(email):
            return jsonify({"error": "Email already registered"}), 400

        # Create new user
        user_model.create_user(name, email, password)
        return jsonify({"message": "User registered successfully"}), 201

    return auth_bp
