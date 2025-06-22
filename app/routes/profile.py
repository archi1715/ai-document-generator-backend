# app/routes/profile.py

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.auth.dependencies import get_current_user
from app.db.mongo import get_user_profiles_collection
from pydantic import BaseModel, EmailStr
from app.db.mongo import get_user_profiles_collection
router = APIRouter(prefix="/api/profile", tags=["User Profile"])
from bson import ObjectId

# Schema for profile creation and update
class PublicUserProfile(BaseModel):
    name: str
    lastname: str
    # dob: str
    age: int
    email: EmailStr
    number: str
    country: str
    state: str
    city: str
    # url: str
@router.get("/user-get")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    email = current_user["email"]
    print(email , "email::::")
    user_profiles_collection = get_user_profiles_collection()

    profile = await user_profiles_collection.find_one({"email": email})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Convert ObjectId to str
    profile["_id"] = str(profile["_id"])
    
    return profile


@router.post("/user-save")
async def save_user_profile(
    profile: PublicUserProfile,
    user=Depends(get_current_user),
    user_profiles_collection=Depends(get_user_profiles_collection)
):
    email = user["email"]

    data = profile.dict()
    data["email"] = email

    # Fetch existing profile
    existing = await user_profiles_collection.find_one({"email": email})
    
    if not existing:
        # New user, set metadata only if it doesn't exist
        data["account_created"] = datetime.utcnow().isoformat()
        data["membership_plan"] = "Free"

    # Preserve existing values (like account_created & last_login) if they exist
    if existing:
        data["account_created"] = existing.get("account_created")
        data["last_login"] = existing.get("last_login")
        data["membership_plan"] = existing.get("membership_plan")

    # Account verification logic
    data["account_verification"] = (
        "Verified" if all(data.get(field) for field in [
            "name", "lastname", "age", "email", "number", "country"
        ]) else "Not Verified"
    )

    # Save to DB
    await get_user_profiles_collection.update_one(
        {"email": email},
        {"$set": data},
        upsert=True
    )

    return {"status": "success", "message": "Profile saved successfully."}


# GET: Fetch profile of currently logged-in user
@router.get("/user-get")
async def get_user_profile(user=Depends(get_current_user)):
    email = user["email"]
    profile = await get_user_profiles_collection.find_one({"email": email})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile["_id"] = str(profile["_id"])  # Convert ObjectId to string
    return profile

# Schema for profile creation and update
class PublicUserProfile(BaseModel):
    name: str
    lastname: str
    dob: str
    age: int
    email: EmailStr
    number: str
    country: str
    state: str
    city: str
    url: str

#  First-time profile creation using public data
@router.post("/user")
async def public_create_user_profile(profile: PublicUserProfile):
    existing = await get_user_profiles_collection.find_one({"email": profile.email})
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists. Use update instead.")

    current_time = datetime.utcnow().isoformat()
    data = profile.dict()
    data["account_created"] = current_time
    data["last_login"] = current_time
    data["membership_plan"] = "Free"
    data["account_verification"] = (
        "Verified" if all(data.get(field) for field in [
            "name", "lastname", "dob", "email", "number", "country"
        ]) else "Not Verified"
    )

    await get_user_profiles_collection.insert_one(data)
    return {"status": "success", "message": "Profile created successfully."}

# Update profile using public data
@router.put("/user-update")
async def public_update_user_profile(profile: PublicUserProfile):
    existing = await get_user_profiles_collection.find_one({"email": profile.email})
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found. Please create first.")

    result = await get_user_profiles_collection.update_one(
        {"email": profile.email},
        {"$set": profile.dict()}
    )

    if result.modified_count > 0:
        return {"status": "success", "message": "Profile updated successfully"}
    else:
        return {"message": "No changes made to the profile"}

