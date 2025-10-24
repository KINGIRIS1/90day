"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth_utils import TokenManager
from bson import ObjectId

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = None
):
    """Extract and validate current user from JWT token"""
    if db is None:
        from server import db as server_db
        db = server_db.db
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    token = credentials.credentials
    payload = TokenManager.decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Retrieve user from database
    users_collection = db["users"]
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    return user


async def require_approved_user(
    current_user: dict = Depends(get_current_user)
):
    """Ensure user has approved status"""
    if current_user["status"] != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {current_user['status']}. Please contact admin."
        )
    
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return current_user


async def require_admin(
    current_user: dict = Depends(require_approved_user)
):
    """Ensure user has admin role"""
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user
