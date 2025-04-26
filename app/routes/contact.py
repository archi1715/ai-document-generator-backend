from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from app.db.mongo import db
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME
router = APIRouter(prefix="/api", tags=["Contact"])
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
contacts_collection = db.get_collection("contacts")

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    subject: str
    message: str

@router.post("/contact")
async def submit_contact(data: ContactRequest):
    await contacts_collection.insert_one(data.dict())
    return {"status": "success", "message": "Message sent"}

