from fastapi import APIRouter, HTTPException, Depends
from app.models.user import UserCreate, LoginRequest
from app.db.mongo import users_collection
from app.auth.auth import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# ✅ Register route (needed!)
@router.post("/register")
async def register(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Match password and confirm password
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    hashed_pwd = hash_password(user.password)
    new_user = {"email": user.email, "password": hashed_pwd}
    await users_collection.insert_one(new_user)

    return {"status": "success", "message": "User registered successfully"}

# ✅ Login route
@router.post("/login")
async def login(login_data: LoginRequest):
    db_user = await users_collection.find_one({"email": login_data.email})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(login_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": db_user["email"]})
    return {"status": "success", "access_token": token, "token_type": "bearer"}

# ✅ Change password route
@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, user=Depends(get_current_user)):
    if not verify_password(data.old_password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    new_hashed = hash_password(data.new_password)
    await users_collection.update_one(
        {"email": user["email"]},
        {"$set": {"password": new_hashed}}
    )

    return {"status": "success", "message": "Password changed successfully"}

