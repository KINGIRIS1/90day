"""
Seed admin user into database
Run this once to create the initial admin account
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from auth_utils import PasswordHasher
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

async def create_admin():
    # Connect to MongoDB
    mongo_url = os.getenv("MONGO_URL")
    client = AsyncIOMotorClient(mongo_url)
    
    # Extract database name from MONGO_URL or use default
    if mongo_url and "/" in mongo_url:
        db_name = mongo_url.split("/")[-1].split("?")[0]
    else:
        db_name = "document_scanner"
    
    db = client[db_name]
    users_collection = db["users"]
    
    # Check if admin already exists
    existing_admin = await users_collection.find_one({"username": "admin"})
    
    if existing_admin:
        print("✅ Admin user already exists")
        return
    
    # Create admin user
    admin_password = "Thommit@19"  # As requested
    hashed_password = PasswordHasher.hash_password(admin_password)
    
    admin_user = {
        "email": "admin@smartdocscan.com",
        "username": "admin",
        "hashed_password": hashed_password,
        "full_name": "Admin",
        "roles": ["admin", "user"],
        "status": "approved",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "approved_at": datetime.now(timezone.utc),
        "approved_by": None
    }
    
    result = await users_collection.insert_one(admin_user)
    print(f"✅ Admin user created successfully!")
    print(f"   Username: admin")
    print(f"   Password: {admin_password}")
    print(f"   User ID: {result.inserted_id}")
    
    # Create unique indexes
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("username", unique=True)
    print("✅ Database indexes created")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
