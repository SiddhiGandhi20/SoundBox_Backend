from werkzeug.security import check_password_hash

class LoginModel:
    def __init__(self, db):
        self.collection = db.signup  # Assuming signup and login share the same collection

    def get_user_by_email(self, email):
        """Retrieve a user by email."""
        return self.collection.find_one({"email": email})

    def check_password(self, stored_password, provided_password):
        """Check if the provided password matches the stored hashed password."""
        return check_password_hash(stored_password, provided_password)
