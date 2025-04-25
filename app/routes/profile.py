# app/routes/profile.py

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.auth.dependencies import get_current_user
from app.db.mongo import user_profiles_collection
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

    # Save to DB (upsert)
    await user_profiles_collection.update_one(
        {"email": email},
        {"$set": data},
        upsert=True
    )

    return {"status": "success", "message": "Profile saved successfully."}


@router.put("/user-update")
async def public_update_user_profile(
    profile: PublicUserProfile,
    current_user: dict = Depends(get_current_user),
    user_profiles_collection = Depends(get_user_profiles_collection)
):
    email = current_user["email"]

    existing = await user_profiles_collection.find_one({"email": email})
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found. Please create first.")

    result = await user_profiles_collection.update_one(
        {"email": email},
        {"$set": profile.dict()}
    )

    if result.modified_count > 0:
        return {"status": "success", "message": "Profile updated successfully"}
    else:
        return {"message": "No changes made to the profile"}

