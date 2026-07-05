

import requests

API_URL = "http://127.0.0.1:5000"


def print_menu():
    print("\n--- Inventory Management CLI ---")
    print("1. View all items")
    print("2. View a single item")
    print("3. Add a new item")
    print("4. Update an item")
    print("5. Delete an item")
    print("6. Look up a product on OpenFoodFacts")
    print("7. Exit")


def view_all_items():
    try:
        response = requests.get(API_URL + "/inventory")
    except requests.exceptions.RequestException:
        print("Could not reach the API. Is the Flask server running?")
        return

    items = response.json()

    if len(items) == 0:
        print("No items in inventory yet.")
        return

    for item in items:
        print(
            f"{item['id']}: {item['product_name']} "
            f"| stock: {item['stock']} | price: {item['price']}"
        )


def view_single_item():
    item_id = input("Enter item id: ")

    try:
        response = requests.get(API_URL + "/inventory/" + item_id)
    except requests.exceptions.RequestException:
        print("Could not reach the API. Is the Flask server running?")
        return

    if response.status_code == 404:
        print("Item not found.")
        return

    item = response.json()
    for key in item:
        print(f"{key}: {item[key]}")


def add_new_item():
    product_name = input("Product name: ")
    brand = input("Brand: ")
    barcode = input("Barcode (optional): ")
    category = input("Category (optional): ")

    price_input = input("Price: ")
    stock_input = input("Stock quantity: ")

    try:
        price = float(price_input)
    except ValueError:
        print("Price must be a number. Setting price to 0.0")
        price = 0.0

    try:
        stock = int(stock_input)
    except ValueError:
        print("Stock must be a whole number. Setting stock to 0")
        stock = 0

    payload = {
        "product_name": product_name,
        "brand": brand,
        "barcode": barcode,
        "category": category,
        "price": price,
        "stock": stock,
    }

    try:
        response = requests.post(API_URL + "/inventory", json=payload)
    except requests.exceptions.RequestException:
        print("Could not reach the API. Is the Flask server running?")
        return

    if response.status_code == 201:
        new_item = response.json()
        print(f"Item added with id {new_item['id']}")
    else:
        print("Failed to add item:", response.json())


def update_existing_item():
    item_id = input("Enter item id to update: ")

    print("Leave a field blank to keep it unchanged.")
    price_input = input("New price: ")
    stock_input = input("New stock quantity: ")

    payload = {}

    if price_input.strip() != "":
        try:
            payload["price"] = float(price_input)
        except ValueError:
            print("Price must be a number, skipping price update.")

    if stock_input.strip() != "":
        try:
            payload["stock"] = int(stock_input)
        except ValueError:
            print("Stock must be a whole number, skipping stock update.")

    if len(payload) == 0:
        print("Nothing to update.")
        return

    try:
        response = requests.patch(API_URL + "/inventory/" + item_id, json=payload)
    except requests.exceptions.RequestException:
        print("Could not reach the API. Is the Flask server running?")
        return

    if response.status_code == 200:
        print("Item updated successfully.")
    elif response.status_code == 404:
        print("Item not found.")
    else:
        print("Failed to update item:", response.json())


def delete_existing_item():
    item_id = input("Enter item id to delete: ")

    try:
        response = requests.delete(API_URL + "/inventory/" + item_id)
    except requests.exceptions.RequestException:
        print("Could not reach the API. Is the Flask server running?")
        return

    if response.status_code == 200:
        print("Item deleted.")
    elif response.status_code == 404:
        print("Item not found.")
    else:
        print("Failed to delete item:", response.json())


def lookup_product():
    print("Search by:")
    print("1. Barcode")
    print("2. Name")
    choice = input("Choice: ")

    params = {}
    if choice == "1":
        params["barcode"] = input("Enter barcode: ")
    elif choice == "2":
        params["name"] = input("Enter product name: ")
    else:
        print("Invalid choice.")
        return

    try:
        response = requests.get(API_URL + "/external/lookup", params=params)
    except requests.exceptions.RequestException:
        print("Could not reach the API. Is the Flask server running?")
        return

    if response.status_code == 404:
        print("Product not found on OpenFoodFacts.")
        return

    if response.status_code != 200:
        print("Something went wrong:", response.json())
        return

    product = response.json()
    for key in product:
        print(f"{key}: {product[key]}")

    add_choice = input("Add this product to inventory? (y/n): ")
    if add_choice.lower() == "y":
        price_input = input("Set a price: ")
        stock_input = input("Set stock quantity: ")

        try:
            product["price"] = float(price_input)
        except ValueError:
            product["price"] = 0.0

        try:
            product["stock"] = int(stock_input)
        except ValueError:
            product["stock"] = 0

        add_response = requests.post(API_URL + "/inventory", json=product)
        if add_response.status_code == 201:
            print("Added to inventory with id", add_response.json()["id"])


def main():
    while True:
        print_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            view_all_items()
        elif choice == "2":
            view_single_item()
        elif choice == "3":
            add_new_item()
        elif choice == "4":
            update_existing_item()
        elif choice == "5":
            delete_existing_item()
        elif choice == "6":
            lookup_product()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")


if __name__ == "__main__":
    main()
