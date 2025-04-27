from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.db.mongo import db 
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME
from app.db.mongo import get_subscribers_collection, initialize_db
router = APIRouter(prefix="/api", tags=["Subscriber"])
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

subscribers_collection = db.get_collection("subscribers")

class SubscribeRequest(BaseModel):
    email: EmailStr



@router.post("/subscribe")
async def create_subscriber(data: SubscribeRequest):
    try:

        subscribers_collection= get_subscribers_collection()
        

        result = await subscribers_collection.insert_one(data.dict())
        
        if result and result.inserted_id:
            return {"status": "success", "message": "Message sent"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save contact message")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting contact: {str(e)}")


