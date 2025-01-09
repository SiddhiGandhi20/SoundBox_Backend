from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

# Constants
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads/smartwatches/')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility function to generate the URL for the uploaded image
def generate_image_url(filename, base_url):
    return f"{base_url}uploads/smartwatches/{filename}"

# Blueprint factory
def create_smartwatch_routes(db):
    smartwatches_bp = Blueprint('smartwatches', __name__)

    # Route: Create a smartwatches item
    @smartwatches_bp.route("/smartwatches", methods=["POST"])
    def create_smartwatches():
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
            smartwatch_data = {"name": name, "price": price, "image_url": image_url}
            result = db.smartwatches.insert_one(smartwatch_data)
            smartwatch_data["_id"] = str(result.inserted_id)

            return jsonify(smartwatch_data), 201
        except Exception as e:
            return jsonify({"message": f"Error creating smartwatch: {str(e)}"}), 500

    # Route: Fetch all smartwatches
    @smartwatches_bp.route("/smartwatches", methods=["GET"])
    def get_all_smartwatches():
        try:
            smartwatches = db.smartwatches.find({}, {"name": 1, "price": 1, "image_url": 1})
            smartwatches_list = [
                {"_id": str(h["_id"]), "name": h["name"], "price": h["price"], "image_url": h["image_url"]}
                for h in smartwatches
            ]
            return jsonify(smartwatches_list), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching smartwatches: {str(e)}"}), 500

    # Route: Fetch smartwatch by ID
    @smartwatches_bp.route("/smartwatches/<id>", methods=["GET"])
    def get_smartwatch_by_id(id):
        try:
            smartwatch = db.smartwatches.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            if not smartwatch:
                return jsonify({"message": "smartwatches not found"}), 404
            smartwatch["_id"] = str(smartwatch["_id"])
            return jsonify(smartwatch), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching smartwatch: {str(e)}"}), 500

    # Route: Update a smartwatch item
    @smartwatches_bp.route("/smartwatches/<id>", methods=["PUT"])
    def update_smartwatches(id):
        try:
            smartwatch = db.smartwatches.find_one({"_id": ObjectId(id)})
            if not smartwatch:
                return jsonify({"message": "smartwatches not found"}), 404

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

            db.smartwatches.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            updated_smartwatch = db.smartwatches.find_one({"_id": ObjectId(id)}, {"name": 1, "price": 1, "image_url": 1})
            updated_smartwatch["_id"] = str(updated_smartwatch["_id"])

            return jsonify(updated_smartwatch), 200
        except Exception as e:
            return jsonify({"message": f"Error updating smartwatch: {str(e)}"}), 500

    # Route: Delete a smartwatch item
    @smartwatches_bp.route("/smartwatches/<id>", methods=["DELETE"])
    def delete_smartwatch(id):
        try:
            result = db.smartwatches.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return jsonify({"message": "smartwatch not found"}), 404
            return jsonify({"message": "smartwatch deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting smartwatch: {str(e)}"}), 500

    @smartwatches_bp.route("/uploads/smartwatches/<filename>")
    def serve_image(filename):
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except FileNotFoundError:
            return jsonify({"message": "File not found"}), 404



    return smartwatches_bp
