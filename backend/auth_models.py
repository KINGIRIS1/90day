"""
Pydantic models for authentication and user management
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        """Ensure username contains only alphanumeric characters and underscores"""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric with optional underscores')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        """Validate password meets minimum security requirements"""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    roles: List[str]
    status: str
    is_active: bool
    created_at: datetime
