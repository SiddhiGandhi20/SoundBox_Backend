from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from bson.objectid import ObjectId
from models.headphone_details_model import HeadphoneDetailsModel
import socket

def create_headphone_details_routes(db, upload_folder):
    details_bp = Blueprint('headphone_details', __name__)

    # Instantiate the headphoneDetailsModel
    details_model = HeadphoneDetailsModel(db)

    # Get the host IP address
    def get_host_ip():
        # This will get the machine's local IP address
        host_ip = socket.gethostbyname(socket.gethostname())
        return host_ip

    # POST: Create a new detail
    @details_bp.route("/headphone-details", methods=["POST"])
    def create_headphone_detail():
        try:
            name = request.form.get("name")
            description = request.form.get("description")
            price = request.form.get("price")
            headphone_id = request.form.get("headphone_id")
            image = request.files.get("image")

            # Validate required fields
            if not all([name, description, price, headphone_id, image]):
                return jsonify({"message": "Missing required fields"}), 400

            # Ensure headphone_id exists in the headphones collection
            if not db.headphones.find_one({"_id": ObjectId(headphone_id)}):
                return jsonify({"message": "Invalid headphone ID"}), 400

            # Save image
            headphones_folder = os.path.join(upload_folder, "headphones")
            if not os.path.exists(headphones_folder):
                os.makedirs(headphones_folder)

            filename = secure_filename(image.filename)
            image_path = os.path.join(headphones_folder, filename)
            image.save(image_path)

            # Construct image URL with host IP address
            host_ip = get_host_ip()
            image_url = f"http://{host_ip}:5000/uploads/headphones/{filename}"  # Assuming your Flask app runs on port 5000

            # Create detail data
            detail_data = {
                "name": name,
                "description": description,
                "price": float(price.replace(",", "")),
                "image_url": image_url,
                "headphone_id": headphone_id
            }

            # Insert into MongoDB
            created_detail = details_model.create_detail(detail_data)
            return jsonify(created_detail), 201
        except Exception as e:
            return jsonify({"message": f"Error creating detail: {str(e)}"}), 500

    # GET: Fetch all details
    @details_bp.route("/headphone-details", methods=["GET"])
    def get_all_headphone_details():
        try:
            details = details_model.get_all_details()
            return jsonify(details), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching details: {str(e)}"}), 500

    # GET: Fetch a detail by ID
    @details_bp.route("/headphone-details/<id>", methods=["GET"])
    def get_headphone_detail_by_id(id):
        try:
            detail = details_model.get_detail_by_id(id)
            if not detail:
                return jsonify({"message": "Detail not found"}), 404
            return jsonify(detail), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching detail: {str(e)}"}), 500

    # PUT: Update a detail by ID
    @details_bp.route("/headphone-details/<id>", methods=["PUT"])
    def update_headphone_detail(id):
        try:
            updated_data = request.form.to_dict()
            if "price" in updated_data:
                updated_data["price"] = float(updated_data["price"].replace(",", ""))

            if "image" in request.files:
                image = request.files.get("image")
                filename = secure_filename(image.filename)
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)
                
                # Construct image URL with host IP address
                host_ip = get_host_ip()
                updated_data["image_url"] = f"http://{host_ip}:5000/uploads/headphones/{filename}"

            updated_detail = details_model.update_detail(id, updated_data)
            if not updated_detail:
                return jsonify({"message": "Detail not found"}), 404
            return jsonify(updated_detail), 200
        except Exception as e:
            return jsonify({"message": f"Error updating detail: {str(e)}"}), 500

    # DELETE: Delete a detail by ID
    @details_bp.route("/headphone-details/<id>", methods=["DELETE"])
    def delete_headphone_detail(id):
        try:
            result = details_model.delete_detail(id)
            if not result:
                return jsonify({"message": "Detail not found"}), 404
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting detail: {str(e)}"}), 500

    return details_bp
