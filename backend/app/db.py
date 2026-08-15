from pymongo import MongoClient
from .config import Config


try:
    client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[Config.MONGO_DB]
except Exception:
    try:
        import mongomock
        client = mongomock.MongoClient()
        db = client[Config.MONGO_DB]
    except Exception:
        client = None
        db = None

complaints = db["complaints"] if db is not None else None
users = db["users"] if db is not None else None


def init_db():
    if complaints is None or users is None:
        return False
    try:
        complaints.create_index("complaint_id", unique=True)
        complaints.create_index("status")
        complaints.create_index("category")
        complaints.create_index("user_id")
        users.create_index("email", unique=True)
        client.admin.command("ping")
    except Exception as exc:
        print(f"MongoDB connection warning: {exc}")
        return False

    # Admin seeding with safe defaults so the app works out of the box.
    import os
    admin_email = os.environ.get("ADMIN_EMAIL", Config.ADMIN_EMAIL)
    admin_password = os.environ.get("ADMIN_PASSWORD", Config.ADMIN_PASSWORD)
    from werkzeug.security import generate_password_hash
    existing = users.find_one({"email": admin_email.lower()})
    if not existing:
        users.insert_one({
            "name": "Administrator",
            "email": admin_email.lower(),
            "phone": "",
            "password_hash": generate_password_hash(admin_password),
            "role": "admin",
            "created_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
        })
    return True
