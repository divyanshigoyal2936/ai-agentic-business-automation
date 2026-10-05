from core.database import customers_collection

def find_customer_by_email(email):
    customer = customers_collection.find_one({"email": email})
    if customer is None:
        return {"error": "Customer not found"}  
    return customer

def get_all_customers():
    customer = list(customers_collection.find())   
    return customer 

def find_customer_by_id(customer_id):
    customer = customers_collection.find_one({"customer_id": customer_id})
    if customer is None:
        return {"error": "Customer not found"}  
    return customer