from flask import Flask, request, jsonify
from capital_gains_bl import process_capital_gains_request

app = Flask(__name__)

@app.route("/capital-gains", methods=["GET"])
def capital_gains():
    try:
        response = process_capital_gains_request(request)
        return response
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"server error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
