from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from app.db.mongo import db

router = APIRouter(prefix="/api", tags=["Feedback"])

feedback_collection = db.get_collection("feedback")

class FeedbackRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

@router.post("/feedback")
async def submit_feedback(data: FeedbackRequest):
    await feedback_collection.insert_one(data.dict())
    return {"status": "success", "message": "Feedback received"}


