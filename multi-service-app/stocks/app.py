from flask import Flask, request, jsonify
from models import Portfolio
from bson import ObjectId  # For handling MongoDB ObjectIds
import os

from utils import validate_json_request
from utils import is_valid_stock_data

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
COLLECTION_NAME = os.getenv("COLLECTION", "default_collection")

app = Flask(__name__)
portfolio = Portfolio(MONGO_URI, COLLECTION_NAME)


@app.route("/stocks", methods=["POST"])
def create_stock():
    if not request.is_json:
        return jsonify({"error": "Expected application/json media type"}), 415

    data = request.get_json()
    if not is_valid_stock_data(data):
        return jsonify({"error": "Malformed data"}), 400

    success,data=validate_json_request(data)
    if not success:
        return jsonify({"error": "Malformed data"}), 400

    stock_id = portfolio.add_stock(data)
    if stock_id is None:
        return jsonify({"error": "Symbol already exists"}), 400

    return jsonify({"id": stock_id}), 201


@app.route("/stocks", methods=["GET"])
def get_stocks():
    try:
        stocks = portfolio.get_all_stocks()
        return jsonify(stocks), 200
    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route("/stocks/<stock_id>", methods=["GET"])
def get_stock(stock_id):
    try:
        stock = portfolio.get_stock(stock_id)
        if not stock:
            return jsonify({"error": "Not found"}), 404
        return jsonify(stock), 200
    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route("/stocks/<stock_id>", methods=["PUT"])
def update_stock(stock_id):
    if not request.is_json:
        return jsonify({"error": "Expected application/json media type"}), 415

    data = request.get_json()


    response = portfolio.update_stock(stock_id, data)

    if response == 400:
        return jsonify({"error": "Malformed data"}), 400
    if response == 404:
        return jsonify({"error": "Not found"}), 404
    if response == 500:
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"id": stock_id}), 200


@app.route("/stocks/<stock_id>", methods=["DELETE"])
def delete_stock(stock_id):
    try:
        if portfolio.delete_stock(stock_id):
            return "", 204
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route("/stock-value/<stock_id>", methods=["GET"])
def get_stock_value(stock_id):
    try:
        value = portfolio.get_stock_value(stock_id)
        if value:
            return jsonify(value), 200
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route("/portfolio-value", methods=["GET"])
def get_portfolio_value():
    try:
        return jsonify(portfolio.get_portfolio_value()), 200
    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route('/kill', methods=['GET'])
def kill_container():
    os._exit(1)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
