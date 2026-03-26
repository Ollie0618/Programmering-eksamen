from entity import Product


def test_product_revenue():
    product = Product("Laptop", "Elektronik", 5000.0, 3)
    assert product.revenue() == 15000.0