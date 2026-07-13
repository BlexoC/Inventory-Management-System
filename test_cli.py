

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, Mock

import cli


@patch("cli.requests.get")
def test_view_all_items_prints_items(mock_get, capsys):
    mock_response = Mock()
    mock_response.json.return_value = [
        {"id": 1, "product_name": "Oat Milk", "stock": 5, "price": 2.5}
    ]
    mock_get.return_value = mock_response

    cli.view_all_items()

    captured = capsys.readouterr()
    assert "Oat Milk" in captured.out


@patch("cli.requests.get")
def test_view_all_items_empty(mock_get, capsys):
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    cli.view_all_items()

    captured = capsys.readouterr()
    assert "No items in inventory yet." in captured.out


@patch("cli.requests.post")
@patch("cli.input")
def test_add_new_item_success(mock_input, mock_post, capsys):
    mock_input.side_effect = [
        "Oat Milk",  # product_name
        "Oatly",  # brand
        "",  # barcode
        "",  # category
        "3.99",  # price
        "10",  # stock
    ]
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 1}
    mock_post.return_value = mock_response

    cli.add_new_item()

    captured = capsys.readouterr()
    assert "Item added with id 1" in captured.out


@patch("cli.requests.post")
@patch("cli.input")
def test_add_new_item_invalid_price_defaults_to_zero(mock_input, mock_post, capsys):
    mock_input.side_effect = [
        "Oat Milk",
        "Oatly",
        "",
        "",
        "not_a_number",
        "10",
    ]
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 2}
    mock_post.return_value = mock_response

    cli.add_new_item()

    captured = capsys.readouterr()
    assert "Price must be a number" in captured.out


@patch("cli.requests.delete")
@patch("cli.input", return_value="1")
def test_delete_existing_item_success(mock_input, mock_delete, capsys):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_delete.return_value = mock_response

    cli.delete_existing_item()

    captured = capsys.readouterr()
    assert "Item deleted." in captured.out


@patch("cli.requests.delete")
@patch("cli.input", return_value="999")
def test_delete_existing_item_not_found(mock_input, mock_delete, capsys):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_delete.return_value = mock_response

    cli.delete_existing_item()

    captured = capsys.readouterr()
    assert "Item not found." in captured.out


@patch("cli.requests.get")
@patch("cli.input")
def test_lookup_product_by_barcode_found(mock_input, mock_get, capsys):
    mock_input.side_effect = ["1", "1234567890", "n"]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "barcode": "1234567890",
        "category": "Beverages",
        "ingredients_text": "Water, almonds",
        "image_url": "",
    }
    mock_get.return_value = mock_response

    cli.lookup_product()

    captured = capsys.readouterr()
    assert "Organic Almond Milk" in captured.out


@patch("cli.requests.get")
@patch("cli.input", return_value="9")
def test_lookup_product_invalid_choice(mock_input, mock_get, capsys):
    cli.lookup_product()

    captured = capsys.readouterr()
    assert "Invalid choice." in captured.out
    mock_get.assert_not_called()
