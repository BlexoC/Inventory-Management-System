

inventory = []
next_id = 1


def get_all_items():
    return inventory


def get_item_by_id(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


def add_item(data):
    """
    Add a new item to the inventory.
    `data` is a dictionary, usually the JSON body from a POST request
    or a product dictionary returned by external_api.py.
    """
    global next_id

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

    return new_item


def update_item(item_id, data):
    """
    Update an existing item with whatever fields are present in `data`.
    Fields that are not included are left unchanged. Returns the
    updated item, or None if no item with that id exists.
    """
    item = get_item_by_id(item_id)

    if item is None:
        return None

    for key in data:
        if key != "id":
            item[key] = data[key]

    return item


def delete_item(item_id):
    item = get_item_by_id(item_id)

    if item is None:
        return False

    inventory.remove(item)
    return True


def clear_all():
    """Reset storage back to empty. Mainly used between test cases."""
    global inventory, next_id
    inventory = []
    next_id = 1
