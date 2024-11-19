"""Example in how to connect to mongoDB and insert a document"""
#  pylint: disable=line-too-long
from pymongo import MongoClient

def insert_data():
    """Inserts data into test"""
    # Connect to MongoDB
    client = MongoClient("mongodb://admin:adminpassword@localhost:27017")
    db = client["e_commerce_db"]

    # Insert document
    product_data = {
        "product_name": "Camiseta Masculina Manga Curta Básica Premium Lisa Green",
        "product_description": "001.10020 Green",
        "SKU": "023000205004",
        "one_time_payment": 52.53,
        "quantity_of_payments": 4,
        "payments_value": "R$ 13,13",
        "product_link": "https://www.harpie.com.br/camiseta-masculina-manga-curta-basica-premium-lisa-green",
        "color": "Verde Escuro",
        "variation": [
            { "size": "P", "in_stock": True },
            { "size": "M", "in_stock": True },
            { "size": "G", "in_stock": True },
            { "size": "GG", "in_stock": True },
            { "size": "XGG", "in_stock": True }
        ],
        "rating": None,
        "number_of_ratings": []
    }

    db.test_data.insert_one(product_data)

if __name__ == "__main__":
    insert_data()
