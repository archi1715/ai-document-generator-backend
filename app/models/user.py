from pydantic import BaseModel, EmailStr
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    

class UserProfile(BaseModel):
    name: str
    lastname: str
    dob: str
    age: str
    email: str
    number: str
    country: str
    state: str
    city: str
    # url: str  # profile picture URL
    #  account_created: Optional[str] = None
    account_created: str
    last_login: str
    membership_plan: str
    account_verification: str
