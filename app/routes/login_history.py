from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List
from app.db.mongo import get_login_history_collection
from app.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Login History"])

class LoginRecord(BaseModel):
    email: str
    timestamp: datetime

@router.get("/login-history", response_model=List[LoginRecord])
async def get_login_history(user=Depends(get_current_user)):
    try:
        collection = get_login_history_collection()
        records = await collection.find(
            {"email": user["email"]}
        ).sort("timestamp", -1).to_list(length=50)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch login history")
