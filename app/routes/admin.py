from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.db.mongo import (
    get_admin_collection,
    get_users_collection,
    get_feedback_collection,
    get_contacts_collection,
    get_subscribers_collection
)
from app.auth.auth import verify_password
from jose import jwt
from app.config import SECRET_KEY

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

# ------------------------
# Admin Login (from MongoDB, using hashed password)
# ------------------------
class AdminLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def admin_login(data: AdminLogin):
    admin_col = get_admin_collection()
    admin = await admin_col.find_one({"email": data.email})
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if not verify_password(data.password, admin["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"sub": data.email}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


# ------------------------
# Get All Users
# ------------------------
@router.get("/users")
async def get_all_users():
    users = []
    cursor = get_users_collection().find({})
    async for user in cursor:
        user["_id"] = str(user["_id"])
        users.append(user)
    return users


# ------------------------
# Get All Feedback
# ------------------------
@router.get("/feedback")
async def get_all_feedback():
    feedbacks = []
    cursor = get_feedback_collection().find({})
    async for item in cursor:
        item["_id"] = str(item["_id"])
        feedbacks.append(item)
    return feedbacks


# ------------------------
# Get All Contacts
# ------------------------
@router.get("/contacts")
async def get_all_contacts():
    contacts = []
    cursor = get_contacts_collection().find({})
    async for item in cursor:
        item["_id"] = str(item["_id"])
        contacts.append(item)
    return contacts


# ------------------------
# Get All Subscribers
# ------------------------
@router.get("/subscribers")
async def get_all_subscribers():
    subscribers = []
    cursor = get_subscribers_collection().find({})
    async for sub in cursor:
        sub["_id"] = str(sub["_id"])
        subscribers.append(sub)
    return subscribers
