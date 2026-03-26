from flask import Flask, render_template, request, redirect
from entity import Product
from database import get_total_revenue
import csv
import openpyxl
from database import (
    create_database,
    get_all_products,
    insert_product,
    delete_product_db,
    get_products_by_category,
    search_products
)

app = Flask(__name__, template_folder="template")
create_database()

@app.route("/")
def index():
    products = get_all_products()
    total_revenue = get_total_revenue()

    return render_template(
        "index.html",
        products=products,
        total_revenue=total_revenue
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        price = float(request.form["price"])
        quantity = int(request.form["quantity"])

        product = Product(name, category, price, quantity)

        insert_product(product)

        return redirect("/")

    return render_template("admin.html")


@app.route("/delete/<int:id>")
def delete_product(id):
    delete_product_db(id)
    return redirect("/")


@app.route("/sammenligning", methods=["GET", "POST"])
def sammenligning():
    result = None

    if request.method == "POST":

        category1 = request.form["category1"]
        category2 = request.form["category2"]

        rows1 = get_products_by_category(category1)
        rows2 = get_products_by_category(category2)

        products1 = [Product(*p[1:]) for p in rows1]
        products2 = [Product(*p[1:]) for p in rows2]

        sold1 = sum(p.quantity for p in products1)
        sold2 = sum(p.quantity for p in products2)

        revenue1 = round(sum(p.revenue() for p in products1), 2)
        revenue2 = round(sum(p.revenue() for p in products2), 2)

        avg_price1 = round(
            sum(p.price for p in products1) / len(products1), 2
        ) if products1 else 0

        avg_price2 = round(
            sum(p.price for p in products2) / len(products2), 2
        ) if products2 else 0

        result = {
            "category1": category1,
            "sold1": sold1,
            "revenue1": revenue1,
            "avg_price1": avg_price1,
            "category2": category2,
            "sold2": sold2,
            "revenue2": revenue2,
            "avg_price2": avg_price2,
            "revenue_difference": abs(revenue1 - revenue2),
            "sold_difference": abs(sold1 - sold2),
            "avg_price_difference": abs(avg_price1 - avg_price2)
        }

    return render_template("sammenligning.html", result=result)


@app.route("/allproducts")
def all_products():
    return render_template(
        "allproducts.html",
        elektronik=get_products_by_category("Elektronik"),
        moebler=get_products_by_category("Møbler"),
        pleje=get_products_by_category("Personlig pleje"),
        toj=get_products_by_category("Tøj")
    )


@app.route("/search")
def search():
    query = request.args.get("query")
    results = search_products(query)
    return render_template("search.html", results=results, query=query)


@app.route("/upload_file", methods=["POST"])
def upload_file():
    file = request.files["file"]

    if not file:
        return redirect("/")

    filename = file.filename.lower()

    # 🔹 CSV
    if filename.endswith(".csv"):
        stream = file.stream.read().decode("latin-1").splitlines()
        csv_reader = csv.DictReader(stream)

        for row in csv_reader:
            product = Product(
                row["name"],
                row["category"],
                float(row["price"]),
                int(row["quantity"])
            )
            insert_product(product)

    # 🔹 Excel
    elif filename.endswith(".xlsx"):
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active

        for row in sheet.iter_rows(min_row=2, values_only=True):
            name, category, price, quantity = row

            product = Product(
                name,
                category,
                float(price),
                int(quantity)
            )
            insert_product(product)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)