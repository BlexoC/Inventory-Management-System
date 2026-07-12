# Inventory Management System

An administrator portal for an e-commerce retail company. It's built as a
Flask REST API backed by an in-memory "database" (a plain Python list),
with a CLI front end to interact with it, and OpenFoodFacts integration
to pull in real product data by barcode or name.

## Project structure

```
inventory_system/
├── app.py                  # Flask API (routes)
├── storage.py               # In-memory data store (list of dicts)
├── external_api.py          # OpenFoodFacts integration
├── cli.py                   # CLI front end that talks to the API
├── requirements.txt
├── tests/
│   ├── test_api.py           # Tests for Flask routes
│   ├── test_external_api.py  # Tests for OpenFoodFacts integration (mocked)
│   └── test_cli.py           # Tests for CLI functions (mocked)
└── README.md
```

## 1. Installation and setup

Requires Python 3.10+.

```bash
# Clone the repo
git clone <your-repo-url>
cd inventory_system

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

If you prefer `pipenv`:

```bash
pipenv install flask requests
pipenv install pytest --dev
pipenv shell
```

### Running the API

```bash
python app.py
```

This starts the Flask dev server (with debug mode on) at
`http://127.0.0.1:5000`.

### Running the CLI

In a **second terminal** (leave the API running in the first one):

```bash
python cli.py
```

### Running the tests

```bash
pytest -v
```

All external HTTP calls (both to our own Flask app and to
OpenFoodFacts) are mocked in the tests, so `pytest` doesn't need the
Flask server running or an internet connection.

## 2. API endpoint details

Each inventory item is stored as a dictionary with this shape:

```json
{
  "id": 1,
  "product_name": "Organic Almond Milk",
  "brand": "Silk",
  "barcode": "1234567890",
  "category": "Beverages",
  "price": 3.5,
  "stock": 10,
  "ingredients_text": "Filtered water, almonds, cane sugar",
  "image_url": "https://..."
}
```

`id` is assigned automatically and can't be set or changed by the client.


### Examples with `curl`

Add an item:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Oat Milk", "brand": "Oatly", "price": 4.0, "stock": 15}'
```

Update stock on item 1:

```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"stock": 25}'
```

Delete item 1:

```bash
curl -X DELETE http://127.0.0.1:5000/inventory/1
```

Look up a product by barcode on OpenFoodFacts:

```bash
curl "http://127.0.0.1:5000/external/lookup?barcode=3017620422003"
```

Look up a product by name:

```bash
curl "http://127.0.0.1:5000/external/lookup?name=peanut+butter"
```

## 3. CLI usage

Once `python cli.py` is running, you get a menu:

```
--- Inventory Management CLI ---
1. View all items
2. View a single item
3. Add a new item
4. Update an item
5. Delete an item
6. Look up a product on OpenFoodFacts
7. Exit
```

- **Option 3** prompts for product name, brand, barcode, category,
  price, and stock, then POSTs it to `/inventory`.
- **Option 4** prompts for an item id, then a new price and/or stock
  (leave blank to leave a field unchanged), and PATCHes `/inventory/<id>`.
- **Option 6** lets you search OpenFoodFacts by barcode or name. If a
  match is found, it's printed to the screen, and you're asked whether
  you'd like to add it straight into inventory (you'll be prompted for
  a price and stock quantity, since OpenFoodFacts doesn't have those).

Invalid input (like typing letters where a number is expected) doesn't
crash the CLI — it prints a message and falls back to a sensible
default (e.g. price defaults to `0.0`).

## 4. Notes on the external API

`external_api.py` wraps two OpenFoodFacts endpoints:

- `GET /api/v2/product/<barcode>.json` — for exact barcode lookups.
- `GET /cgi/search.pl?search_terms=<name>` — for name-based search
  (returns the first match).

Both functions return a simplified dictionary with just the fields our
inventory cares about (`product_name`, `brand`, `barcode`, `category`,
`ingredients_text`, `image_url`), or `None` if the product wasn't
found or the request failed for any reason (timeout, connection error,
non-200 response, etc.). The rest of the app never has to deal with
OpenFoodFacts's raw response format.

## 5. Testing approach

- **`test_api.py`** uses Flask's built-in test client to hit every
  route and check status codes and JSON bodies, including error cases
  (missing fields, item not found).
- **`test_external_api.py`** mocks `requests.get` with
  `unittest.mock.patch` so tests don't depend on OpenFoodFacts being
  reachable, and cover the found/not-found/error-handling paths.
- **`test_cli.py`** mocks both `requests` and the built-in `input()`
  function so CLI flows can be tested without a real terminal or
  network connection, checking what gets printed with `capsys`.

## Known limitations

- Data is stored in memory and resets every time the Flask app
  restarts. Swapping `storage.py` for a real database (e.g. SQLite +
  SQLAlchemy) would be the natural next step.
- No authentication — this is meant as an internal admin tool.
