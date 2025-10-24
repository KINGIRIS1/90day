"""
Seed admin user into database
Run this once to create the initial admin account
Can be run via: python3 seed_admin.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from auth_utils import PasswordHasher
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def create_admin():
    # Connect to MongoDB
    mongo_url = os.getenv("MONGO_URL")
    
    if not mongo_url:
        print("❌ MONGO_URL not found in environment!")
        return
    
    print(f"Connecting to: {mongo_url[:30]}...")
    
    client = AsyncIOMotorClient(mongo_url)
    
    # Get database name from MONGO_URL or environment
    db_name = os.getenv("DB_NAME")
    if not db_name:
        # Extract from MONGO_URL
        if "/" in mongo_url:
            db_name = mongo_url.split("/")[-1].split("?")[0]
        else:
            db_name = "document_scanner_db"
    
    print(f"Using database: {db_name}")
    
    db = client[db_name]
    users_collection = db["users"]
    
    # Check if admin already exists
    existing_admin = await users_collection.find_one({"username": "admin"})
    
    if existing_admin:
        print("⚠️  Admin user already exists!")
        print(f"   Username: {existing_admin['username']}")
        print(f"   Email: {existing_admin['email']}")
        print(f"   Status: {existing_admin['status']}")
        
        # Ask to recreate
        response = input("Do you want to recreate admin? (yes/no): ")
        if response.lower() != 'yes':
            client.close()
            return
        
        await users_collection.delete_one({"username": "admin"})
        print("🗑️  Old admin deleted")
    
    # Create admin user
    admin_password = "Thommit@19"
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
    print(f"   Database: {db_name}")
    print(f"   Username: admin")
    print(f"   Password: {admin_password}")
    print(f"   User ID: {result.inserted_id}")
    
    # Create unique indexes
    try:
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("username", unique=True)
        print("✅ Database indexes created")
    except Exception as e:
        print(f"⚠️  Indexes may already exist: {e}")
    
    # Verify password
    verify_user = await users_collection.find_one({"username": "admin"})
    if verify_user:
        verify_result = PasswordHasher.verify_password(admin_password, verify_user["hashed_password"])
        print(f"✅ Password verification: {verify_result}")
    
    client.close()
    print("\n🎉 Admin setup complete! You can now login with admin/Thommit@19")

if __name__ == "__main__":
    print("=" * 60)
    print("ADMIN USER SEED SCRIPT")
    print("=" * 60)
    asyncio.run(create_admin())
