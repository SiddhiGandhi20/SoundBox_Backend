import jwt
import datetime
from flask import Blueprint, request, jsonify
import re
from models.adminlogin_model import AdminModel

# Blueprint setup
admin_bp = Blueprint("admin", __name__)

# Directly define the SECRET_KEY here
SECRET_KEY = "your-secret-key"  # Set your secret key here

def setup_admin_routes(db):
    admin_model = AdminModel(db)

    # Admin signup route
    @admin_bp.route("/adminsignup", methods=["POST"])
    def admin_signup():
        """API endpoint to register a new admin."""
        data = request.get_json()

        # Extract data from request
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        # Input validation
        if not (name and email and password):
            return jsonify({"error": "All fields are required"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):  # Validate email format
            return jsonify({"error": "Invalid email address"}), 400

        # Check for duplicate email
        if admin_model.is_email_registered(email):
            return jsonify({"error": "Email already registered"}), 400

        # Create new admin
        admin_model.create_admin(name, email, password)
        return jsonify({"message": "Admin registered successfully"}), 201

    # Admin login route
    @admin_bp.route("/adminlogin", methods=["POST"])
    def admin_login():
        """API endpoint to log in an admin."""
        data = request.get_json()

        # Extract data from request
        email = data.get("email")
        password = data.get("password")

        # Input validation
        if not (email and password):
            return jsonify({"error": "Email and password are required"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):  # Validate email format
            return jsonify({"error": "Invalid email address"}), 400

        # Check if admin exists and password matches
        admin = admin_model.get_admin_by_email(email)
        if not admin or not admin_model.check_password(admin["password"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate JWT token
        payload = {
            "admin_id": str(admin["_id"]),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({"message": "Admin login successful", "token": token}), 200

    return admin_bp
