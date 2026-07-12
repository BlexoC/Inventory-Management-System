import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# --- storage ---

inventory = []
next_id = 1


def get_item_by_id(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


# --- external API (OpenFoodFacts) ---

OFF_BASE_URL = "https://world.openfoodfacts.org"


def fetch_by_barcode(barcode):
    """Look up one product by its barcode. Returns a dict, or None if not found."""

    url = OFF_BASE_URL + "/api/v2/product/" + str(barcode) + ".json"

    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()

    if data.get("status") != 1:
        return None

    product = data["product"]

    return {
        "product_name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "barcode": barcode,
        "category": product.get("categories", ""),
        "ingredients_text": product.get("ingredients_text", ""),
        "image_url": product.get("image_url", ""),
    }


def fetch_by_name(name):
    """Search for a product by name, return the first result. Returns a dict, or None."""

    url = OFF_BASE_URL + "/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()
    products = data.get("products", [])

    if len(products) == 0:
        return None

    product = products[0]

    return {
        "product_name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "barcode": product.get("code", ""),
        "category": product.get("categories", ""),
        "ingredients_text": product.get("ingredients_text", ""),
        "image_url": product.get("image_url", ""),
    }


# --- routes ---

@app.route("/inventory", methods=["GET"])
def get_all_items():
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = get_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    if not data.get("product_name"):
        return jsonify({"error": "product_name is required"}), 400

    new_item = {
        "id": next_id,
        "product_name": data.get("product_name", ""),
        "brand": data.get("brand", ""),
        "barcode": data.get("barcode", ""),
        "category": data.get("category", ""),
        "price": data.get("price", 0.0),
        "stock": data.get("stock", 0),
        "ingredients_text": data.get("ingredients_text", ""),
        "image_url": data.get("image_url", ""),
    }
    inventory.append(new_item)
    next_id += 1

    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    item = get_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    for key in data:
        if key != "id":
            item[key] = data[key]

    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = get_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": "Item deleted"}), 200


@app.route("/external/lookup", methods=["GET"])
def lookup_external_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if not barcode and not name:
        return jsonify({"error": "Provide a barcode or a name to search"}), 400

    result = fetch_by_barcode(barcode) if barcode else fetch_by_name(name)

    if result is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)