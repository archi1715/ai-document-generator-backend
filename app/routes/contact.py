from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from app.db.mongo import db

router = APIRouter(prefix="/api", tags=["Contact"])

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

