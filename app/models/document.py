from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentHistory(BaseModel):
    id: Optional[str] = Field(alias="_id")
    title: str
    content: str
    created_at: datetime