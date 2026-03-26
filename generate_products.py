import sqlite3
import random

conn = sqlite3.connect("products.db")
cursor = conn.cursor()

categories = {
    "Elektronik": [
        "iPhone", "Samsung TV", "Laptop", "AirPods", "Playstation", "Tablet", "Smartwatch"
    ],
    "Møbler": [
        "Sofa", "Spisebord", "Kontorstol", "Seng", "Reol", "Skrivebord", "Skab"
    ],
    "Personlig pleje": [
        "Shampoo", "Tandbørste", "Parfume", "Hudcreme", "Barbermaskine", "Hårtørrer"
    ],
    "Tøj": [
        "T-shirt", "Jeans", "Jakke", "Sneakers", "Hoodie", "Kasket", "Shorts"
    ]
}

products = []

for category in categories:
    for i in range(25):  # 25 produkter pr kategori

        name = random.choice(categories[category]) + " " + str(i)

        price = random.randint(10, 20)

        quantity = random.randint(2, 3)

        products.append((name, category, price, quantity))


cursor.executemany("""
INSERT INTO products (name, category, price, quantity)
VALUES (?, ?, ?, ?)
""", products)

conn.commit()
conn.close()

print("100 produkter genereret!")