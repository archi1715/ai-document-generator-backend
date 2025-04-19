from fastapi import APIRouter, HTTPException  # Removed Depends (no longer needed)
from app.models.user import UserCreate
from app.db.mongo import users_collection
from app.auth.auth import hash_password, verify_password, create_access_token

from pydantic import BaseModel  # ✅ New import for JSON schema

router = APIRouter(prefix="/auth", tags=["Auth"])

# ✅ Define JSON login input model
class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)
    new_user = {"email": user.email, "password": hashed_pwd}
    await users_collection.insert_one(new_user)
    return {"status": "success", "message": "User registered successfully"}

# ✅ Modified login to use JSON
@router.post("/login")
async def login(login_data: LoginRequest):
    db_user = await users_collection.find_one({"email": login_data.email})
    
    if not db_user or not verify_password(login_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": db_user["email"]})
    
    return {"status": "success", "access_token": token, "token_type": "bearer"}

# user: UserLogin