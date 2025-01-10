from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from bson.objectid import ObjectId
from models.smartwatch_details_model import SmartwatchDetailsModel
import socket

def create_smartwatch_details_routes(db, upload_folder):
    details_bp = Blueprint('smartwatch_details', __name__)

    # Instantiate the smartwatchDetailsModel
    details_model = SmartwatchDetailsModel(db)

    # Get the host IP address
    def get_host_ip():
        host_ip = socket.gethostbyname(socket.gethostname())
        return host_ip

    # POST: Create a new detail
    @details_bp.route("/smartwatch-details", methods=["POST"])
    def create_smartwatch_detail():
        try:
            name = request.form.get("name")
            description = request.form.get("description")
            price = request.form.get("price")
            smartwatch_id = request.form.get("smartwatch_id")
            image = request.files.get("image")

            # Validate required fields
            if not all([name, description, price, smartwatch_id, image]):
                return jsonify({"message": "Missing required fields"}), 400

            # Ensure smartwatch_id exists in the smartwatches collection
            if not db.smartwatches.find_one({"_id": ObjectId(smartwatch_id)}):
                return jsonify({"message": "Invalid smartwatch ID"}), 400

            # Save image
            smartwatches_folder = os.path.join(upload_folder, "smartwatches")
            if not os.path.exists(smartwatches_folder):
                os.makedirs(smartwatches_folder)

            filename = secure_filename(image.filename)
            image_path = os.path.join(smartwatches_folder, filename)
            image.save(image_path)

            # Construct image URL with host IP address
            host_ip = get_host_ip()
            image_url = f"http://{host_ip}:5000/uploads/smartwatches/{filename}"  # Assuming your Flask app runs on port 5000

            # Create detail data
            detail_data = {
                "name": name,
                "description": description,
                "price": float(price.replace(",", "")),
                "image_url": image_url,
                "smartwatch_id": smartwatch_id
            }

            # Insert into MongoDB
            created_detail = details_model.create_detail(detail_data)
            
            if created_detail:
                return jsonify(created_detail), 201  # Return the response with the ID
            else:
                return jsonify({"message": "Error creating detail"}), 500
        except Exception as e:
            return jsonify({"message": f"Error creating detail: {str(e)}"}), 500

    # GET: Fetch all details
    @details_bp.route("/smartwatch-details", methods=["GET"])
    def get_all_smartwatch_details():
        try:
            details = details_model.get_all_details()
            return jsonify(details), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching details: {str(e)}"}), 500

    # GET: Fetch a detail by ID
    @details_bp.route("/smartwatch-details/<id>", methods=["GET"])
    def get_smartwatch_detail_by_id(id):
        try:
            detail = details_model.get_detail_by_id(id)
            if not detail:
                return jsonify({"message": "Detail not found"}), 404
            return jsonify(detail), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching detail: {str(e)}"}), 500

    # PUT: Update a detail by ID
    @details_bp.route("/smartwatch-details/<id>", methods=["PUT"])
    def update_smartwatch_detail(id):
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
                updated_data["image_url"] = f"http://{host_ip}:5000/uploads/smartwatches/{filename}"

            updated_detail = details_model.update_detail(id, updated_data)
            if not updated_detail:
                return jsonify({"message": "Detail not found"}), 404
            return jsonify(updated_detail), 200
        except Exception as e:
            return jsonify({"message": f"Error updating detail: {str(e)}"}), 500

    # DELETE: Delete a detail by ID
    @details_bp.route("/smartwatch-details/<id>", methods=["DELETE"])
    def delete_smartwatch_detail(id):
        try:
            result = details_model.delete_detail(id)
            if not result:
                return jsonify({"message": "Detail not found"}), 404
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting detail: {str(e)}"}), 500

    return details_bp
