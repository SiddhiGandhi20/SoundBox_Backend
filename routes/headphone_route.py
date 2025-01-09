from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

# Constants
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/headphones/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility function to generate the URL for the uploaded image
def generate_image_url(filename, base_url):
    return f"{base_url}uploads/headphones/{filename}"

# Blueprint factory
def create_headphone_routes(db):
    headphones_bp = Blueprint('headphones', __name__)

    # Route: Create a headphones item
    @headphones_bp.route("/headphones", methods=["POST"])
    def create_headphones():
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
            headphone_data = {"name": name, "price": price, "image_url": image_url}
            result = db.headphones.insert_one(headphone_data)
            headphone_data["_id"] = str(result.inserted_id)

            return jsonify(headphone_data), 201
        except Exception as e:
            return jsonify({"message": f"Error creating headphone: {str(e)}"}), 500

    # Route: Fetch all headphones
    @headphones_bp.route("/headphones", methods=["GET"])
    def get_all_headphones():
        try:
            headphones = db.headphones.find({}, {"name": 1, "price": 1, "image_url": 1})
            headphones_list = [
                {"_id": str(h["_id"]), "name": h["name"], "price": h["price"], "image_url": h["image_url"]}
                for h in headphones
            ]
            return jsonify(headphones_list), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching headphones: {str(e)}"}), 500

    # Route: Fetch headphone by ID
    @headphones_bp.route("/headphones/<id>", methods=["GET"])
    def get_headphone_by_id(id):
        try:
            headphone = db.headphones.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            if not headphone:
                return jsonify({"message": "headphones not found"}), 404
            headphone["_id"] = str(headphone["_id"])
            return jsonify(headphone), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching headphone: {str(e)}"}), 500

    # Route: Update a headphone item
    @headphones_bp.route("/headphones/<id>", methods=["PUT"])
    def update_headphones(id):
        try:
            headphone = db.headphones.find_one({"_id": ObjectId(id)})
            if not headphone:
                return jsonify({"message": "headphones not found"}), 404

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

            db.headphones.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            updated_headphone = db.headphones.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            updated_headphone["_id"] = str(updated_headphone["_id"])

            return jsonify(updated_headphone), 200
        except Exception as e:
            return jsonify({"message": f"Error updating headphone: {str(e)}"}), 500

    # Route: Delete a headphone item
    @headphones_bp.route("/headphones/<id>", methods=["DELETE"])
    def delete_headphone(id):
        try:
            result = db.headphones.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return jsonify({"message": "headphone not found"}), 404
            return jsonify({"message": "headphone deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting headphone: {str(e)}"}), 500

    @headphones_bp.route("/uploads/headphones/<filename>")
    def serve_image(filename):
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except FileNotFoundError:
            return jsonify({"message": "File not found"}), 404



    return headphones_bp
