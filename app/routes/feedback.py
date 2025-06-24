from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.db.mongo import db
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.mongo import get_feedback_collection, initialize_db
from app.config import MONGO_URI, DATABASE_NAME
router = APIRouter(prefix="/api", tags=["Feedback"])
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
feedback_collection = db.get_collection("feedback")
from app.db.mongo import get_feedback_collection

router = APIRouter(prefix="/api", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

@router.post("/feedback")
async def submit_feedback(data: FeedbackRequest):
    await get_feedback_collection.insert_one(data.dict())
    return {"status": "success", "message": "Feedback received"}

@router.post("/feedback")
async def submit_feedback(data: FeedbackRequest):
    try:
        # Get the contacts collection
        feedback_collection = get_feedback_collection()

        result = await feedback_collection.insert_one(data.dict())
        
        if result and result.inserted_id:
            return {"status": "success", "message": "Message sent"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save contact message")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting contact: {str(e)}")


