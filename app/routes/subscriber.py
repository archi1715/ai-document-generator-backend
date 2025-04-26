from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.db.mongo import db 
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME
router = APIRouter(prefix="/api", tags=["Subscriber"])
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

subscribers_collection = db.get_collection("subscribers")

class SubscribeRequest(BaseModel):
    email: EmailStr

@router.post("/subscribe")
async def create_subscriber(data: SubscribeRequest):
    existing = await subscribers_collection.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed")
    await subscribers_collection.insert_one(data.dict())
    return {"status": "success", "message": "Subscribed successfully"}

