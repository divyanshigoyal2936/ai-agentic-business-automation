from core.database import  customers_collection

result = customers_collection.insert_many([
  {
    "customer_id": 18734,
    "name": "suzy Doe",
    "email": "suzy.doe@example.com",
    "phone": "123-456-7890",
    "address": "123 Main St, Anytown, USA",
    "created_at": "2023-01-01T00:00:00Z"
  },
  {
    "customer_id": 18735,
    "name": "john Doe",
    "email": "john.doe@example.com",
    "phone": "098-765-4321",
    "address": "456 Oak Ave, Somewhere, USA",
    "created_at": "2023-01-01T00:00:00Z"
  },
  {
    "customer_id": 18736,
    "name": "jane Smith",
    "email": "jane.smith@example.com",
    "phone": "555-123-4567",
    "address": "789 Pine Rd, Elsewhere, USA",
    "created_at": "2023-01-01T00:00:00Z"
  }
])

print(f"Inserted {len(result.inserted_ids)} customers into the database.")

