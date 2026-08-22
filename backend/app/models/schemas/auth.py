from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[str] = "analyst"

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
