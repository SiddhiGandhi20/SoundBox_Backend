from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import PyMongo

class AdminModel:
    def __init__(self, db):
        self.collection = db.adminlogin  # Collection name is admin_signup

    def is_email_registered(self, email):
        """Check if the email is already registered."""
        return self.collection.find_one({"email": email})

    def create_admin(self, name, email, password):
        """Insert a new admin into the database."""
        hashed_password = generate_password_hash(password)
        admin_data = {
            "name": name,
            "email": email,
            "password": hashed_password
        }
        self.collection.insert_one(admin_data)
        return True

    def get_admin_by_email(self, email):
        """Retrieve an admin by email."""
        return self.collection.find_one({"email": email})

    def check_password(self, stored_password, provided_password):
        """Check if the provided password matches the stored hashed password."""
        return check_password_hash(stored_password, provided_password)
