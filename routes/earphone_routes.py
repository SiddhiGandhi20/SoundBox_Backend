from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

# Constants
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/earphones/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility function to generate the URL for the uploaded image
def generate_image_url(filename, base_url):
    return f"{base_url}uploads/earphones/{filename}"

# Blueprint factory
def create_earphones_routes(db):
    earphones_bp = Blueprint('earphones', __name__)

    # Route: Create a earphones item
    @earphones_bp.route("/earphones", methods=["POST"])
    def create_earphones():
        try:
            name = request.form.get("name")
            price = request.form.get("price")
            image = request.files.get("image")

            if not all([name, price, image]):
                return jsonify({"message": "Missing required fields"}), 400

            try:
                price = float(price.replace(",", ""))
            except ValueError:
                return jsonify({"message": "Invalid price format"}), 400

            if not allowed_file(image.filename):
                return jsonify({"message": "Invalid image file type"}), 400

            # Save the image
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)

            # Generate image URL
            base_url = request.host_url
            image_url = generate_image_url(filename, base_url)

            # Insert into database
            earphone_data = {"name": name, "price": price, "image_url": image_url}
            result = db.earphones.insert_one(earphone_data)
            earphone_data["_id"] = str(result.inserted_id)

            return jsonify(earphone_data), 201
        except Exception as e:
            return jsonify({"message": f"Error creating earphone: {str(e)}"}), 500

    # Route: Fetch all earphones
    @earphones_bp.route("/earphones", methods=["GET"])
    def get_all_earphones():
        try:
            earphones = db.earphones.find({}, {"name": 1, "price": 1, "image_url": 1})
            earphones_list = [
                {"_id": str(h["_id"]), "name": h["name"], "price": h["price"], "image_url": h["image_url"]}
                for h in earphones
            ]
            return jsonify(earphones_list), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching earphones: {str(e)}"}), 500

    # Route: Fetch earphone by ID
    @earphones_bp.route("/earphones/<id>", methods=["GET"])
    def get_earphone_by_id(id):
        try:
            earphone = db.earphones.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            if not earphone:
                return jsonify({"message": "earphones not found"}), 404
            earphone["_id"] = str(earphone["_id"])
            return jsonify(earphone), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching earphone: {str(e)}"}), 500

    # Route: Update a earphone item
    @earphones_bp.route("/earphones/<id>", methods=["PUT"])
    def update_earphones(id):
        try:
            earphone = db.earphones.find_one({"_id": ObjectId(id)})
            if not earphone:
                return jsonify({"message": "earphones not found"}), 404

            updated_data = request.form.to_dict()
            if "price" in updated_data:
                updated_data["price"] = float(updated_data["price"].replace(",", ""))

            if "image" in request.files:
                image = request.files["image"]
                if not allowed_file(image.filename):
                    return jsonify({"message": "Invalid image file type"}), 400

                filename = secure_filename(image.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(image_path)
                base_url = request.host_url
                updated_data["image_url"] = generate_image_url(filename, base_url)

            db.earphones.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            updated_earphone = db.earphones.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            updated_earphone["_id"] = str(updated_earphone["_id"])

            return jsonify(updated_earphone), 200
        except Exception as e:
            return jsonify({"message": f"Error updating earphone: {str(e)}"}), 500

    # Route: Delete a earphone item
    @earphones_bp.route("/earphones/<id>", methods=["DELETE"])
    def delete_earphone(id):
        try:
            result = db.earphones.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return jsonify({"message": "earphone not found"}), 404
            return jsonify({"message": "earphone deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting earphone: {str(e)}"}), 500

    @earphones_bp.route("/uploads/earphones/<filename>")
    def serve_image(filename):
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except FileNotFoundError:
            return jsonify({"message": "File not found"}), 404



    return earphones_bp
