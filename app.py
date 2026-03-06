from flask import Flask, render_template, request, redirect
import sqlite3
from entity import Product
from database import create_database

app = Flask(__name__, template_folder="template")
create_database()

def get_db():
    return sqlite3.connect("products.db")


@app.route("/")
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return render_template("index.html", products=products)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        price = float(request.form["price"])
        quantity = int(request.form["quantity"])

        product = Product(name, category, price, quantity)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, category, price, quantity)
            VALUES (?, ?, ?, ?)
        """, (product.name, product.category, product.price, product.quantity))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("admin.html")


@app.route("/delete/<int:id>")
def delete_product(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/comparison", methods=["GET", "POST"])
def comparison():
    result = None

    if request.method == "POST":
        cat1 = request.form["category1"]
        cat2 = request.form["category2"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(price * quantity) FROM products WHERE category = ?", (cat1,))
        sum1 = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(price * quantity) FROM products WHERE category = ?", (cat2,))
        sum2 = cursor.fetchone()[0] or 0

        conn.close()

        result = (cat1, sum1, cat2, sum2)

    return render_template("comparison.html", result=result)


@app.route("/allproducts")
def all_products():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE category = 'Elektronik'")
    elektronik = cursor.fetchall()

    cursor.execute("SELECT * FROM products WHERE category = 'Møbler'")
    moebler = cursor.fetchall()

    cursor.execute("SELECT * FROM products WHERE category = 'Personlig pleje'")
    pleje = cursor.fetchall()

    cursor.execute("SELECT * FROM products WHERE category = 'Tøj'")
    toj = cursor.fetchall()

    conn.close()

    return render_template(
        "allproducts.html",
        elektronik=elektronik,
        moebler=moebler,
        pleje=pleje,
        toj=toj
    )


if __name__ == "__main__":
    app.run(debug=True)