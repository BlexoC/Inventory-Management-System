

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, Mock

import requests

import external_api


@patch("external_api.requests.get")
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

    result = external_api.fetch_by_barcode("1234567890")

    assert result["product_name"] == "Organic Almond Milk"
    assert result["brand"] == "Silk"
    assert result["barcode"] == "1234567890"


@patch("external_api.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": 0}
    mock_get.return_value = mock_response

    result = external_api.fetch_by_barcode("0000000000")
    assert result is None


@patch("external_api.requests.get")
def test_fetch_by_barcode_bad_status_code(mock_get):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = external_api.fetch_by_barcode("1234567890")
    assert result is None


@patch("external_api.requests.get")
def test_fetch_by_barcode_request_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError()

    result = external_api.fetch_by_barcode("1234567890")
    assert result is None


@patch("external_api.requests.get")
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

    result = external_api.fetch_by_name("peanut butter")
    assert result["product_name"] == "Peanut Butter"
    assert result["barcode"] == "111222333"


@patch("external_api.requests.get")
def test_fetch_by_name_no_results(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"products": []}
    mock_get.return_value = mock_response

    result = external_api.fetch_by_name("nonexistent product xyz")
    assert result is None
