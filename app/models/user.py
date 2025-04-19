from pydantic import BaseModel, EmailStr
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    

class UserProfile(BaseModel):
    name: str
    lastname: str
    dob: str
    age: Optional[str] = None 
    email: str
    number: str
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    url: Optional[str] = None 
    #  account_created: Optional[str] = None
    account_created: str
    last_login: str
    membership_plan: str
    account_verification: str
