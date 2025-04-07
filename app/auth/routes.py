from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate, UserLogin
from app.db.mongo import users_collection
from app.auth.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)
    new_user = {"email": user.email, "password": hashed_pwd}
    await users_collection.insert_one(new_user)
    return {"status": "success", "message": "User registered successfully"}

@router.post("/login")
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.email})
    return {"status": "success", "access_token": token, "token_type": "bearer"}
