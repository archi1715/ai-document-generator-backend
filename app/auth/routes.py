# from fastapi import APIRouter, HTTPException  # Removed Depends (no longer needed)
# from app.models.user import UserCreate
# from app.db.mongo import users_collection
# from app.auth.auth import hash_password, verify_password, create_access_token

# from pydantic import BaseModel  # ✅ New import for JSON schema

# router = APIRouter(prefix="/auth", tags=["Auth"])

# # ✅ Define JSON login input model
# class LoginRequest(BaseModel):
#     email: str
#     password: str

# @router.post("/register")
# async def register(user: UserCreate):
#     existing_user = await users_collection.find_one({"email": user.email})
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     hashed_pwd = hash_password(user.password)
#     new_user = {"email": user.email, "password": hashed_pwd}
#     await users_collection.insert_one(new_user)
#     return {"status": "success", "message": "User registered successfully"}

# # ✅ Modified login to use JSON
# @router.post("/login")
# async def login(login_data: LoginRequest):
#     db_user = await users_collection.find_one({"email": login_data.email})
#     print(db_user)
#     if not db_user or not verify_password(login_data.password, db_user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     token = create_access_token({"sub": db_user["email"]})
    
#     return {"status": "success", "access_token": token, "token_type": "bearer"}

# # user: UserLogin


# File: app/auth/routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.models.user import UserCreate
from app.auth.auth import hash_password, verify_password, create_access_token
import logging

# Import get_collection function instead of direct collection reference
from app.db.mongo import get_users_collection

# Set up logging
logger = logging.getLogger("app.auth.routes")

router = APIRouter(prefix="/auth", tags=["Auth"])

# Define JSON login input model
class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(user: UserCreate):

    users_collection = get_users_collection()
    
    if users_collection is None:
        logger.error("Users collection is None during registration")
        raise HTTPException(status_code=500, detail="Database connection error")
    
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = hash_password(user.password)
    new_user = {"email": user.email, "password": hashed_pwd}
    
    try:
        result = await users_collection.insert_one(new_user)
        logger.info(f"User registered with ID: {result.inserted_id}")
        return {"status": "success", "message": "User registered successfully"}
    except Exception as e:
        logger.error(f"Error during user registration: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")

@router.post("/login")
async def login(login_data: LoginRequest):
    # Get fresh reference to collection
    users_collection = get_users_collection()
    
    if users_collection is None:
        logger.error("Users collection is None during login")
        raise HTTPException(status_code=500, detail="Database connection error")
    
    logger.debug(f"Attempting login for email: {login_data.email}")
    
    try:
        db_user = await users_collection.find_one({"email": login_data.email})
        
        if not db_user:
            logger.warning(f"Login attempt failed: User not found - {login_data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        if not verify_password(login_data.password, db_user["password"]):
            logger.warning(f"Login attempt failed: Invalid password for {login_data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        token = create_access_token({"sub": db_user["email"]})
        logger.info(f"Login successful for user: {login_data.email}")
        
        return {"status": "success", "access_token": token, "token_type": "bearer"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Login operation failed")