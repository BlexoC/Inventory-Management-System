import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, Mock

import pytest
import requests

import app as flask_app_module


def reset_inventory():
    flask_app_module.inventory.clear()
    flask_app_module.next_id = 1


@pytest.fixture
def client():
    reset_inventory()
    flask_app_module.app.config["TESTING"] = True
    with flask_app_module.app.test_client() as test_client:
        yield test_client
    reset_inventory()


# --- /inventory routes ---

def test_get_all_items_empty(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert response.get_json() == []


def test_add_item(client):
    payload = {
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "price": 3.5,
        "stock": 10,
    }
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data["id"] == 1
    assert data["product_name"] == "Organic Almond Milk"
    assert data["stock"] == 10


def test_add_item_missing_name(client):
    response = client.post("/inventory", json={"brand": "Silk"})
    assert response.status_code == 400


def test_add_item_no_json_body(client):
    response = client.post("/inventory", data="not json")
    assert response.status_code == 400


def test_get_single_item(client):
    client.post("/inventory", json={"product_name": "Oat Milk"})
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Oat Milk"


def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_update_item(client):
    client.post("/inventory", json={"product_name": "Oat Milk", "stock": 5})
    response = client.patch("/inventory/1", json={"stock": 20})
    assert response.status_code == 200
    assert response.get_json()["stock"] == 20


def test_update_item_not_found(client):
    response = client.patch("/inventory/999", json={"stock": 20})
    assert response.status_code == 404


def test_update_item_no_json_body(client):
    client.post("/inventory", json={"product_name": "Oat Milk"})
    response = client.patch("/inventory/1", data="not json")
    assert response.status_code == 400


def test_update_item_cannot_change_id(client):
    client.post("/inventory", json={"product_name": "Oat Milk"})
    response = client.patch("/inventory/1", json={"id": 999, "stock": 3})
    assert response.status_code == 200
    assert response.get_json()["id"] == 1


def test_delete_item(client):
    client.post("/inventory", json={"product_name": "Oat Milk"})
    response = client.delete("/inventory/1")
    assert response.status_code == 200

    followup = client.get("/inventory/1")
    assert followup.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


# --- /external/lookup route ---

def test_lookup_requires_barcode_or_name(client):
    response = client.get("/external/lookup")
    assert response.status_code == 400


def test_lookup_by_barcode_not_found(client, monkeypatch):
    monkeypatch.setattr(flask_app_module, "fetch_by_barcode", lambda barcode: None)
    response = client.get("/external/lookup?barcode=0000000000")
    assert response.status_code == 404


def test_lookup_by_barcode_found(client, monkeypatch):
    fake_product = {
        "product_name": "Peanut Butter",
        "brand": "Skippy",
        "barcode": "111222333",
        "category": "",
        "ingredients_text": "",
        "image_url": "",
    }
    monkeypatch.setattr(flask_app_module, "fetch_by_barcode", lambda barcode: fake_product)
    response = client.get("/external/lookup?barcode=111222333")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Peanut Butter"


def test_lookup_by_name_found(client, monkeypatch):
    fake_product = {
        "product_name": "Oat Milk",
        "brand": "Oatly",
        "barcode": "",
        "category": "",
        "ingredients_text": "",
        "image_url": "",
    }
    monkeypatch.setattr(flask_app_module, "fetch_by_name", lambda name: fake_product)
    response = client.get("/external/lookup?name=oat+milk")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Oat Milk"


# --- fetch_by_barcode / fetch_by_name (OpenFoodFacts integration) ---

@patch("app.requests.get")
def test_fetch_by_barcode_found(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "categories": "Beverages",
            "ingredients_text": "Filtered water, almonds, cane sugar",
            "image_url": "http://example.com/image.jpg",
        },
    }
    mock_get.return_value = mock_response

    result = flask_app_module.fetch_by_barcode("1234567890")

    assert result["product_name"] == "Organic Almond Milk"
    assert result["brand"] == "Silk"
    assert result["barcode"] == "1234567890"


@patch("app.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": 0}
    mock_get.return_value = mock_response

    result = flask_app_module.fetch_by_barcode("0000000000")
    assert result is None


@patch("app.requests.get")
def test_fetch_by_barcode_bad_status_code(mock_get):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = flask_app_module.fetch_by_barcode("1234567890")
    assert result is None


@patch("app.requests.get")
def test_fetch_by_barcode_request_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError()

    result = flask_app_module.fetch_by_barcode("1234567890")
    assert result is None


@patch("app.requests.get")
def test_fetch_by_name_found(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "products": [
            {
                "product_name": "Peanut Butter",
                "brands": "Skippy",
                "code": "111222333",
            }
        ]
    }
    mock_get.return_value = mock_response

    result = flask_app_module.fetch_by_name("peanut butter")
    assert result["product_name"] == "Peanut Butter"
    assert result["barcode"] == "111222333"


@patch("app.requests.get")
def test_fetch_by_name_no_results(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"products": []}
    mock_get.return_value = mock_response

    result = flask_app_module.fetch_by_name("nonexistent product xyz")
    assert result is None