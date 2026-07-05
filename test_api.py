

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

import app as flask_app_module
import storage


@pytest.fixture
def client():
    storage.clear_all()
    flask_app_module.app.config["TESTING"] = True
    with flask_app_module.app.test_client() as test_client:
        yield test_client
    storage.clear_all()


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


def test_delete_item(client):
    client.post("/inventory", json={"product_name": "Oat Milk"})
    response = client.delete("/inventory/1")
    assert response.status_code == 200

    followup = client.get("/inventory/1")
    assert followup.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


def test_lookup_requires_barcode_or_name(client):
    response = client.get("/external/lookup")
    assert response.status_code == 400
