from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.models.user import UserCreate
from app.db.mongo import users_collection
from app.auth.auth import hash_password, verify_password, create_access_token
from fastapi import Depends
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

# ✅ JSON model for login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# ✅ Register route (no auth needed)
@router.post("/register")
async def register(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)
    new_user = {
        "email": user.email,
        "password": hashed_pwd
    }
    await users_collection.insert_one(new_user)

    return {
        "status": "success",
        "message": "User registered successfully"
    }

# ✅ Login route (accepts JSON)
@router.post("/login")
async def login(login_data: LoginRequest):
    try:
        db_user = await users_collection.find_one({"email": login_data.email})
        print("DB user:", db_user)

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        is_valid = verify_password(login_data.password, db_user["password"])
        print("Password match:", is_valid)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token({"sub": db_user["email"]})
        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer"
        }

    except Exception as e:
        print("Login Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, user=Depends(get_current_user)):
    # 1. Match the old password
    if not verify_password(data.old_password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # 2. Hash new password
    new_hashed = hash_password(data.new_password)

    # 3. Update MongoDB
    await users_collection.update_one(
        {"email": user["email"]},
        {"$set": {"password": new_hashed}}
    )

    return {"status": "success", "message": "Password changed successfully"}
