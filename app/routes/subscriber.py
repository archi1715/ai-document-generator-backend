from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.db.mongo import subscribers_collection

router = APIRouter(prefix="/api", tags=["Subscriber"])


class SubscribeRequest(BaseModel):
    email: EmailStr

@router.post("/subscribe")
async def create_subscriber(data: SubscribeRequest):
    existing = await subscribers_collection.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed")
    await subscribers_collection.insert_one(data.dict())
    return {"status": "success", "message": "Subscribed successfully"}

