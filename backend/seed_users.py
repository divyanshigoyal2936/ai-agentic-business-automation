import bcrypt
from core.database import users_collection


def hash_password(password):
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


users_collection.insert_many([
    {
        "email": "agent@company.com",
        "password_hash": hash_password("agent123"),
        "role": "support_agent"
    },
    {
        "email": "manager@company.com",
        "password_hash": hash_password("manager123"),
        "role": "manager"
    }
])