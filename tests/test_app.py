import importlib
import sqlite3
import sys
import pytest


def insert_product(db_path, name, category, price, quantity):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO products (name, category, price, quantity)
        VALUES (?, ?, ?, ?)
        """,
        (name, category, price, quantity),
    )
    conn.commit()
    conn.close()


@pytest.fixture
def app_module(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    for module_name in ["app", "database"]:
        if module_name in sys.modules:
            del sys.modules[module_name]

    import app
    importlib.reload(app)

    app.app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app_module):
    return app_module.app.test_client()


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_admin_get_returns_200(client):
    response = client.get("/admin")
    assert response.status_code == 200


def test_admin_post_creates_product_and_redirects(client):
    response = client.post(
        "/admin",
        data={
            "name": "Laptop",
            "category": "Elektronik",
            "price": "4999.99",
            "quantity": "2",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, category, price, quantity FROM products")
    result = cursor.fetchall()
    conn.close()

    assert len(result) == 1
    assert result[0] == ("Laptop", "Elektronik", 4999.99, 2)


def test_delete_product_removes_product_and_redirects(client):
    insert_product("products.db", "Sofa", "Møbler", 2500.0, 1)

    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products WHERE name = ?", ("Sofa",))
    product_id = cursor.fetchone()[0]
    conn.close()

    response = client.get(f"/delete/{product_id}")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    deleted_product = cursor.fetchone()
    conn.close()

    assert deleted_product is None


def test_search_finds_matching_product(client):
    insert_product("products.db", "Laptop", "Elektronik", 5000.0, 2)
    insert_product("products.db", "Sofa", "Møbler", 3000.0, 1)

    response = client.get("/search?query=Laptop")

    assert response.status_code == 200
    assert b"Laptop" in response.data
    assert b"Sofa" not in response.data


def test_allproducts_returns_200(client):
    insert_product("products.db", "Laptop", "Elektronik", 5000.0, 2)
    insert_product("products.db", "Sofa", "Møbler", 3000.0, 1)
    insert_product("products.db", "Shampoo", "Personlig pleje", 50.0, 10)
    insert_product("products.db", "Jakke", "Tøj", 800.0, 4)

    response = client.get("/allproducts")

    assert response.status_code == 200


def test_sammenligning_calculates_correct_result(app_module):
    insert_product("products.db", "Laptop", "Elektronik", 5000.0, 2)
    insert_product("products.db", "Mus", "Elektronik", 200.0, 5)
    insert_product("products.db", "Sofa", "Møbler", 3000.0, 1)

    captured = {}

    def fake_render_template(template_name, **context):
        captured["template"] = template_name
        captured["context"] = context
        return "OK"

    app_module.render_template = fake_render_template

    with app_module.app.test_request_context(
        "/sammenligning",
        method="POST",
        data={"category1": "Elektronik", "category2": "Møbler"},
    ):
        result = app_module.sammenligning()

    assert result == "OK"
    assert captured["template"] == "sammenligning.html"

    data = captured["context"]["result"]

    assert data["category1"] == "Elektronik"
    assert data["category2"] == "Møbler"

    assert data["sold1"] == 7
    assert data["sold2"] == 1

    assert data["revenue1"] == 11000.0
    assert data["revenue2"] == 3000.0

    assert data["avg_price1"] == 2600.0
    assert data["avg_price2"] == 3000.0

    assert data["revenue_difference"] == 8000.0
    assert data["sold_difference"] == 6
    assert data["avg_price_difference"] == 400.0