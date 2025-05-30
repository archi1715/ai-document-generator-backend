from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
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


