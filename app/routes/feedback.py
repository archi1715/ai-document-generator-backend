from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from app.db.mongo import db
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME
router = APIRouter(prefix="/api", tags=["Feedback"])
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
feedback_collection = db.get_collection("feedback")

class FeedbackRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

@router.post("/feedback")
async def submit_feedback(data: FeedbackRequest):
    await feedback_collection.insert_one(data.dict())
    return {"status": "success", "message": "Feedback received"}


