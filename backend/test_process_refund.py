from tools.order_tools import process_refund
from core.database import orders_collection

print("=== BEFORE ===")
order_before = orders_collection.find_one({"order_id": 101})
print(order_before)

print("\n=== PROCESSING REFUND ===")
result = process_refund(101)
print(result)

print("\n=== AFTER ===")
order_after = orders_collection.find_one({"order_id": 101})
print(order_after)