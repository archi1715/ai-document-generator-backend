from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
<<<<<<< HEAD
from app.db.mongo import db 
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME
from app.db.mongo import get_subscribers_collection, initialize_db
=======
from app.db.mongo import get_subscribers_collection

>>>>>>> develop
router = APIRouter(prefix="/api", tags=["Subscriber"])
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]


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

    existing = await get_subscribers_collection.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed")
    await get_subscribers_collection.insert_one(data.dict())
    return {"status": "success", "message": "Subscribed successfully"}

