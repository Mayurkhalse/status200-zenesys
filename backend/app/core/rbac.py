from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token

security_scheme = HTTPBearer(auto_error=True)

class UserSession:
    def __init__(self, user_id: str, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> UserSession:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Invalid or expired access token", "detail": None}},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserSession(
        user_id=payload["sub"],
        email=payload["email"],
        role=payload.get("role", "viewer")
    )

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: UserSession = Depends(get_current_user)) -> UserSession:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": {"code": "FORBIDDEN", "message": f"Role '{current_user.role}' lacks required permissions", "detail": None}}
            )
        return current_user
    return role_checker
