from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.db.database import get_mongo_db
from app.core.security import (
    get_password_hash, verify_password, create_access_token,
    generate_refresh_token, hash_refresh_token
)
from app.core.rbac import get_current_user, UserSession
from app.models.schemas.auth import (
    UserRegisterRequest, UserLoginRequest, TokenResponse,
    RefreshTokenRequest, UserResponse
)
from app.services.audit_service import audit_service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register_user(req: UserRegisterRequest):
    db = get_mongo_db()
    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "USER_EXISTS", "message": "User with this email already exists", "detail": None}}
        )

    user_doc = {
        "email": req.email,
        "password_hash": get_password_hash(req.password),
        "full_name": req.full_name,
        "role": req.role if req.role in ["admin", "analyst", "viewer"] else "viewer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    res = await db.users.insert_one(user_doc)
    user_id = str(res.inserted_id)

    await audit_service.log_action(user_id, "register", "user", user_id)

    return UserResponse(
        user_id=user_id,
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        role=user_doc["role"]
    )

@router.post("/login", response_model=TokenResponse)
async def login_user(req: UserLoginRequest):
    db = get_mongo_db()
    user = await db.users.find_one({"email": req.email})
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password", "detail": None}}
        )

    user_id = str(user["_id"])
    access_token = create_access_token(user_id=user_id, email=user["email"], role=user["role"])
    raw_refresh = generate_refresh_token()
    token_hash = hash_refresh_token(raw_refresh)

    refresh_doc = {
        "token_hash": token_hash,
        "user_id": user["_id"],
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "revoked": False,
        "created_at": datetime.now(timezone.utc)
    }
    await db.refresh_tokens.insert_one(refresh_doc)

    await audit_service.log_action(user_id, "login", "user", user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        token_type="bearer",
        expires_in=15 * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(req: RefreshTokenRequest):
    db = get_mongo_db()
    token_hash = hash_refresh_token(req.refresh_token)
    stored = await db.refresh_tokens.find_one({"token_hash": token_hash, "revoked": False})
    
    if not stored or stored["expires_at"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_REFRESH_TOKEN", "message": "Refresh token is invalid or expired", "detail": None}}
        )

    # Revoke old token (rotation)
    await db.refresh_tokens.update_one({"_id": stored["_id"]}, {"$set": {"revoked": True}})

    user = await db.users.find_one({"_id": stored["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = str(user["_id"])
    new_access = create_access_token(user_id=user_id, email=user["email"], role=user["role"])
    new_raw_refresh = generate_refresh_token()
    new_hash = hash_refresh_token(new_raw_refresh)

    await db.refresh_tokens.insert_one({
        "token_hash": new_hash,
        "user_id": user["_id"],
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "revoked": False,
        "created_at": datetime.now(timezone.utc)
    })

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_raw_refresh,
        token_type="bearer",
        expires_in=15 * 60
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(req: RefreshTokenRequest, current_user: UserSession = Depends(get_current_user)):
    db = get_mongo_db()
    token_hash = hash_refresh_token(req.refresh_token)
    await db.refresh_tokens.update_one({"token_hash": token_hash}, {"$set": {"revoked": True}})
    await audit_service.log_action(current_user.user_id, "logout", "user", current_user.user_id)
    return None

@router.get("/users/me", response_model=UserResponse)
async def get_me(current_user: UserSession = Depends(get_current_user)):
    db = get_mongo_db()
    user = await db.users.find_one({"_id": ObjectId(current_user.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        user_id=str(user["_id"]),
        email=user["email"],
        full_name=user.get("full_name", ""),
        role=user.get("role", "viewer")
    )
