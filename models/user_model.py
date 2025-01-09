from werkzeug.security import generate_password_hash
from flask_pymongo import PyMongo

class UserModel:
    def __init__(self, db):
        self.collection = db.signup

    def is_email_registered(self, email):
        """Check if the email is already registered."""
        return self.collection.find_one({"email": email})

    def create_user(self, name, email, password):
        """Insert a new user into the database."""
        hashed_password = generate_password_hash(password)
        user_data = {
            "name": name,
            "email": email,
            "password": hashed_password
        }
        self.collection.insert_one(user_data)
        return True
