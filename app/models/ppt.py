from pydantic import BaseModel
from typing import List, Optional

class PromptRequest(BaseModel):
    prompt: str
    num_slides: Optional[int] = 10  # Default to 10 if not provided

class SlideOutline(BaseModel):
    slide_number: int
    title: str
    description: str

class UpdateSlidePromptRequest(BaseModel):
    slide_number: int
    new_prompt: str

class SlideContent(BaseModel):
    slide_number: int
    title: str
    bullet_points: List[str]  
    image_prompt: Optional[str] = None

    

