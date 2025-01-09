from pymongo.errors import PyMongoError
from bson import ObjectId

class HeadphoneDetailsModel:
    def __init__(self, db):
        self.collection = db["headphone_details"]

    def create_detail(self, detail_data):
        try:
            item = {
                "name": detail_data["name"],
                "price": float(detail_data["price"]),
                "image_url": detail_data["image_url"],
                "description": detail_data["description"],
                "headphone_id": detail_data["headphone_id"]
            }
            result = self.collection.insert_one(item)
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"Error creating item: {e}")
            return None

    def get_all_details(self):
        try:
            items = self.collection.find()
            return [
                {
                    "_id": str(item["_id"]),
                    "name": item["name"],
                    "price": item["price"],
                    "image_url": item["image_url"],
                    "description": item["description"],
                    "headphone_id": item["headphone_id"]
                }
                for item in items
            ]
        except PyMongoError as e:
            print(f"Error retrieving items: {e}")
            return []

    def get_detail_by_id(self, item_id):
        try:
            item = self.collection.find_one({"_id": ObjectId(item_id)})
            if item:
                return {
                    "id": str(item["_id"]),
                    "name": item["name"],
                    "price": item["price"],
                    "image_url": item["image_url"],
                    "description": item["description"],
                    "headphone_id": item["headphone_id"]
                }
            return None
        except PyMongoError as e:
            print(f"Error retrieving item: {e}")
            return None

    def update_detail(self, item_id, update_data):
        try:
            if "price" in update_data:
                update_data["price"] = float(update_data["price"])

            result = self.collection.update_one(
                {"_id": ObjectId(item_id)}, {"$set": update_data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            print(f"Error updating item: {e}")
            return False

    def delete_detail(self, item_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(item_id)})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Error deleting item: {e}")
            return False
