from datetime import datetime,timedelta
from core.database import orders_collection
orders_collection.insert_many([
    {
        "order_id": 101,
        "customer_id": 18734,
        "product_name": "Wireless Mouse",
        "order_date": datetime.now() - timedelta(days=3),
        "status": "Delivered"
    },
    {
        "order_id": 102,
        "customer_id": 18735,   
        "product_name": "Bluetooth Headphones",
        "order_date": datetime.now() - timedelta(days=10),
        "status": "Delivered"
    },
    {
        "order_id": 103,
        "customer_id": 18736,
        "product_name": "Smartphone",
        "order_date": datetime.now() - timedelta(days=6),
        "status": "Delivered"
    },
])           