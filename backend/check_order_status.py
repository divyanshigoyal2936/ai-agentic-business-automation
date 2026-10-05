from core.database import orders_collection
order = orders_collection.find_one({"order_id": 103})
print(order)