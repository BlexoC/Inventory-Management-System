

from flask import Flask, jsonify, request

import storage
import external_api

app = Flask(__name__)


@app.route("/inventory", methods=["GET"])
def get_all_items():
    items = storage.get_all_items()
    return jsonify(items), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = storage.get_item_by_id(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "product_name" not in data or data["product_name"] == "":
        return jsonify({"error": "product_name is required"}), 400

    new_item = storage.add_item(data)
    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    updated_item = storage.update_item(item_id, data)

    if updated_item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(updated_item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    deleted = storage.delete_item(item_id)

    if not deleted:
        return jsonify({"error": "Item not found"}), 404

    return jsonify({"message": "Item deleted"}), 200


@app.route("/external/lookup", methods=["GET"])
def lookup_external_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if not barcode and not name:
        return jsonify({"error": "Provide a barcode or a name to search"}), 400

    if barcode:
        result = external_api.fetch_by_barcode(barcode)
    else:
        result = external_api.fetch_by_name(name)

    if result is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)
