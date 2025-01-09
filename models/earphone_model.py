from pymongo.errors import PyMongoError
from bson import ObjectId

class EarphoneModel:
    def __init__(self, db):
        self.collection = db["earphones"]

    def create_item(self, name, price, image_url):
        try:
            item = {
                "name": name,
                "price": float(price.replace(",", "")),
                "image_url": image_url
            }
            result = self.collection.insert_one(item)
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"Error creating item: {e}")
            return None

    def get_all_items(self):
        try:
            items = self.collection.find()
            return [
                {
                    "_id": str(item["_id"]),
                    "id": str(item["_id"]),
                    "name": item["name"],
                    "price": item["price"],
                    "image_url": item["image_url"]
                }
                for item in items
            ]
        except PyMongoError as e:
            print(f"Error retrieving items: {e}")
            return []

    def get_item_by_id(self, item_id):
        try:
            item = self.collection.find_one({"_id": ObjectId(item_id)})
            if item:
                return {
                    "id": str(item["_id"]),
                    "name": item["name"],
                    "price": item["price"],
                    "image_url": item["image_url"]
                }
            return None
        except PyMongoError as e:
            print(f"Error retrieving item: {e}")
            return None

    def update_item(self, item_id, update_data):
        try:
            if "price" in update_data:
                update_data["price"] = float(update_data["price"].replace(",", ""))

            result = self.collection.update_one(
                {"_id": ObjectId(item_id)}, {"$set": update_data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            print(f"Error updating item: {e}")
            return False

    def delete_item(self, item_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(item_id)})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Error deleting item: {e}")
            return False
