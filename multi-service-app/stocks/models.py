from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from api_client import get_stock_price  # Assuming this is defined elsewhere
from utils import validate_json_request
from utils import is_valid_stock_data


class Portfolio:
    def __init__(self, mongodb_uri, collection_name):
        self.client = MongoClient(mongodb_uri)
        self.db = self.client.get_default_database()
        self.collection = self.db[collection_name]
        self.used_symbols = set(self._load_used_symbols())

    def _load_used_symbols(self):
        """Load all used symbols from the database"""
        return [stock['symbol'] for stock in self.collection.find({}, {'symbol': 1})]

    def add_stock(self, stock_data):
        if stock_data["symbol"].upper() in self.used_symbols:
            return None

        stock = {
            "name": stock_data.get("name", "NA"),
            "symbol": stock_data["symbol"].upper(),
            "purchase price": round(float(stock_data.get("purchase price", 0)), 2),
            "purchase date": stock_data.get("purchase date", "NA"),
            "shares": int(stock_data["shares"])
        }

        result = self.collection.insert_one(stock)
        stock_id = str(result.inserted_id)
        self.used_symbols.add(stock["symbol"])
        return stock_id

    def get_stock_value(self, stock_id):
        try:
            stock = self.collection.find_one({"_id": ObjectId(stock_id)})
            if not stock:
                return None

            current_price = get_stock_price(stock["symbol"])
            return {
                "symbol": stock["symbol"],
                "ticker": current_price,
                "stock value": round(current_price * stock["shares"], 2)
            }
        except Exception as e:
            print(f"Error in get_stock_value: {e}")
            return None

    def get_portfolio_value(self):
        try:
            total_value = 0
            for stock in self.collection.find():
                current_price = get_stock_price(stock["symbol"])
                total_value += current_price * stock["shares"]

            return {
                "date": datetime.now().strftime("%d-%m-%Y"),
                "portfolio value": round(total_value, 2)
            }
        except Exception as e:
            print(f"Error in get_portfolio_value: {e}")
            return {"error": "Unable to calculate portfolio value"}

    def get_all_stocks(self):
        stocks = []
        for stock in self.collection.find():
            stock["id"] = str(stock.pop("_id"))
            stocks.append(stock)
        return stocks

    def get_stock(self, stock_id):
        try:
            stock = self.collection.find_one({"_id": ObjectId(stock_id)})
            if stock:
                stock["id"] = str(stock.pop("_id"))
                return stock
            return None
        except Exception:
            return None

    def delete_stock(self, stock_id):
        try:
            object_id = ObjectId(stock_id)
            stock = self.collection.find_one({"_id": object_id})
            if not stock:
                return False

            result = self.collection.delete_one({"_id": object_id})
            if result.deleted_count > 0:
                self.used_symbols.remove(stock["symbol"])
                return True
            return False
        except Exception:
            return False

    def update_stock(self, stock_id, stock_data):

        if not is_valid_stock_data(stock_data, require_all_fields=True):
            print("failed is_valid_stock_data ")
            return 400

        response,stock_data = validate_json_request(stock_data)

        if not response:
            print("failed validate_json_request ")
            return 400

        try:
            object_id = ObjectId(stock_id)
            existing_stock = self.collection.find_one({"_id": object_id})
            if not existing_stock:
                return 404

            new_symbol = stock_data["symbol"].upper()
            if (new_symbol != existing_stock["symbol"] and
                    self.collection.find_one({"symbol": new_symbol, "_id": {"$ne": object_id}})):
                return 400

            update_data = {
                "name": stock_data["name"],
                "symbol": new_symbol,
                "purchase price": round(float(stock_data["purchase price"]), 2),
                "purchase date": stock_data["purchase date"],
                "shares": int(stock_data["shares"])
            }

            result = self.collection.update_one({"_id": object_id}, {"$set": update_data})

            if result.matched_count == 0:
                return 404  # ID not found



            if new_symbol != existing_stock["symbol"]:
                self.used_symbols.remove(existing_stock["symbol"])
                self.used_symbols.add(new_symbol)

            return 200  # Successfully updated


        except Exception as e:
            print(f"Error in update_stock: {str(e)}")
            return 500


    def kill_service(self):
        """Endpoint to test service failure and recovery"""
        import os
        os._exit(1)