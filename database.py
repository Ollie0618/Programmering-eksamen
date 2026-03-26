import sqlite3


def get_db():
    return sqlite3.connect("products.db")

# Opret database
def create_database():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# Hent alle produkter (A-Z)
def get_all_products():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products ORDER BY name ASC")
    data = cursor.fetchall()

    conn.close()
    return data


# Indsæt produkt
def insert_product(product):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, category, price, quantity)
        VALUES (?, ?, ?, ?)
    """, (product.name, product.category, product.price, product.quantity))

    conn.commit()
    conn.close()


# Slet produkt
def delete_product_db(product_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

    conn.commit()
    conn.close()


# Hent produkter efter kategori
def get_products_by_category(category):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE category = ?
        ORDER BY name ASC
    """, (category,))

    data = cursor.fetchall()

    conn.close()
    return data


# Søg produkter
def search_products(query):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE name LIKE ? OR category LIKE ?
    """, (f"%{query}%", f"%{query}%"))

    data = cursor.fetchall()

    conn.close()
    return data

# Total omtjening
def get_total_revenue():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(price * quantity) FROM products")
    result = cursor.fetchone()[0]

    conn.close()

    return result if result else 0