

import requests

BASE_URL = "https://world.openfoodfacts.org"
TIMEOUT = 10


def fetch_by_barcode(barcode):
    """
    Look up a single product by its barcode using the v2 product endpoint.
    Returns a simplified dictionary of product details, or None if the
    product was not found or the request failed.
    """
    url = BASE_URL + "/api/v2/product/" + str(barcode) + ".json"

    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()

    if data.get("status") != 1:
        return None

    return _simplify_product(data["product"], barcode=barcode)


def fetch_by_name(name):
    """
    Search for a product by name using the search endpoint, and return
    the first matching result. Returns a simplified dictionary of
    product details, or None if nothing matched or the request failed.
    """
    url = BASE_URL + "/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1,
    }

    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()
    products = data.get("products", [])

    if len(products) == 0:
        return None

    first_product = products[0]
    return _simplify_product(first_product, barcode=first_product.get("code", ""))


def _simplify_product(product, barcode=""):
    """
    OpenFoodFacts product objects contain dozens of fields we don't
    need. Pull out just the ones relevant to our inventory.
    """
    return {
        "product_name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "barcode": barcode,
        "category": product.get("categories", ""),
        "ingredients_text": product.get("ingredients_text", ""),
        "image_url": product.get("image_url", ""),
    }
