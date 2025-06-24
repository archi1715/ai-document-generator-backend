from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.db.mongo import db
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME
from app.db.mongo import get_contacts_collection, initialize_db
router = APIRouter(prefix="/api", tags=["Contact"])
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
contacts_collection = db.get_collection("contacts")
from app.db.mongo import get_contacts_collection

router = APIRouter(prefix="/api", tags=["Contact"])

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    subject: str
    message: str

@router.post("/contact")
async def submit_contact(data: ContactRequest):
    try:
        # Get the contacts collection
        contacts_collection = get_contacts_collection()

        result = await contacts_collection.insert_one(data.dict())
        
        if result and result.inserted_id:
            return {"status": "success", "message": "Message sent"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save contact message")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting contact: {str(e)}")