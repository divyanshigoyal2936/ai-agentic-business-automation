from datetime import datetime
from core.database import orders_collection

def check_refund_eligibility(order_id):
    order = orders_collection.find_one({"order_id": order_id})

    if not order:
        return {"error": "Order not found"}

    order_date = order["order_date"]
    day_since_order = (datetime.now() - order_date).days

    if day_since_order <= 7:
        eligible = True
    else:
        eligible = False

    return {
        "order_id": order_id,
        "day_since_order": day_since_order,
        "eligible": eligible
    }   

def process_refund(order_id):
    order = orders_collection.find_one({"order_id": order_id})
    
    if not order:
        return {"error": "Order not found"}
    
    orders_collection.update_one(
        {"order_id": order_id},
        {"$set": {"status": "refunded"}}
    )
    
    return {"order_id": order_id, "status": "refunded", "message": "Refund processed successfully"}     