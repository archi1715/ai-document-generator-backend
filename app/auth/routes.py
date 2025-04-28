from fastapi import APIRouter, HTTPException, Depends
from app.models.user import UserCreate, LoginRequest,ResetPasswordRequest,ChangePasswordRequest,ForgotPasswordRequest
from app.db.mongo import get_users_collection
from app.db.mongo import get_user_profiles_collection
from app.auth.auth import hash_password, verify_password, create_access_token
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.auth.dependencies import get_current_user
from pydantic import BaseModel, EmailStr
from jose import jwt  
from app.config import SECRET_KEY  
from datetime import timedelta
from datetime import datetime

# Set up logging
logger = logging.getLogger("app.auth.routes")
router = APIRouter(prefix="/auth", tags=["Auth"])

async def send_welcome_email(to_email: str):
    sender_email = "darshan.trks015@gmail.com"
    sender_password = "vwlz nemv etyt kdab"


    subject = "🎉 Welcome to AI Doc Generator!"
    
    body = """
    <html>
    <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color:#f4f4f4;">
        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; margin:auto; background-color:#ffffff; border-radius:10px; overflow:hidden;">
            <tr style="background-color:#4f46e5;">
                <td style="padding:20px; text-align:center;">
                    <h2 style="color:#ffffff; margin:0;">Welcome to AI Doc Generator 👋</h2>
                </td>
            </tr>
            <tr>
                <td style="padding:30px; color:#333333;">
                    <p style="font-size:16px;">Hi there,</p>
                    <p style="font-size:16px; line-height:1.6;">
                        Thanks for joining <strong>AI Doc Generator</strong>! 🚀<br/>
                        We're excited to have you on board. Your journey to effortless documentation starts now.
                    </p>
                    <p style="font-size:16px;">
                        If you have any questions, feel free to reply to this email. We’re here to help!
                    </p>
                    <a href="https://your-website.com" style="display:inline-block; margin-top:20px; padding:10px 20px; background-color:#4f46e5; color:white; text-decoration:none; border-radius:5px;">
                        Get Started
                    </a>
                </td>
            </tr>
            <tr>
                <td style="padding:20px; text-align:center; font-size:12px; color:#aaaaaa;">
                    &copy; 2025 AI Doc Generator • All rights reserved
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        print("Email sending failed:", e)
        return False
    
    
@router.post("/register")
async def register(user: UserCreate):
    users_collection = get_users_collection()
    user_profiles_collection = get_user_profiles_collection()
    
    # Check DB
    if users_collection is None or user_profiles_collection is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and insert into users collection
    hashed_pwd = hash_password(user.password)
    new_user = {"email": user.email, "password": hashed_pwd}
    
    try:
        result = await users_collection.insert_one(new_user)

        # Create default profile in user_profiles_collection
        now = datetime.utcnow().isoformat()

        default_profile = {
            "email": user.email,
            "name": "",
            "lastname": "",
            # "dob": "",
            "age": 0,
            "number": "",
            "country": "",
            "state": "",
            "city": "",
            "url": "",
            "account_created": now,
            "last_login": now,
            "membership_plan": "Free",
            "account_verification": "Not-verified"
        }

        await user_profiles_collection.insert_one(default_profile)

        # Send welcome email
        await send_welcome_email(user.email)

        return {"status": "success", "message": "User registered successfully"}
    
    except Exception as e:
        logger.error(f"Error during user registration: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")

    # hashed_pwd = hash_password(user.password)
    # new_user = {
    #     "email": user.email,
    #     "password": hashed_pwd
    # }
    # await users_collection.insert_one(new_user)

    # return {
    #     "status": "success",
    #     "message": "User registered successfully"
    # }


@router.post("/login")
async def login(login_data: LoginRequest):
    users_collection = get_users_collection()
    user_profiles_collection = get_user_profiles_collection()
    
    if users_collection is None or user_profiles_collection is None:
        logger.error("Database connection error during login")
        raise HTTPException(status_code=500, detail="Database connection error")

    logger.debug(f"Attempting login for email: {login_data.email}")
    
    try:
        db_user = await users_collection.find_one({"email": login_data.email})
        print("DB user:", db_user)

        if not db_user:
            logger.warning(f"Login failed: User not found - {login_data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        if not verify_password(login_data.password, db_user["password"]):
            logger.warning(f"Login failed: Incorrect password for {login_data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Update last_login timestamp
        await user_profiles_collection.update_one(
            {"email": login_data.email},
            {"$set": {"last_login": datetime.utcnow().isoformat()}}
        )

        token = create_access_token({"sub": db_user["email"]})
        logger.info(f"Login successful for user: {login_data.email}")
        
        return {"status": "success", "access_token": token, "token_type": "bearer"}
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Login operation failed")


@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, user=Depends(get_current_user)):
     if not verify_password(data.old_password, user["password"]):
         raise HTTPException(status_code=400, detail="Incorrect old password")
 
     new_hashed = hash_password(data.new_password)

     await get_users_collection.update_one(
         {"email": user["email"]},
         {"$set": {"password": new_hashed}}
     )
 
     return {"status": "success", "message": "Password changed successfully"}
 
 
 # Forgot Password API (send reset token)
@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    user = await get_users_collection.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_access_token(
        {"sub": user["email"]},
        expires_delta=timedelta(minutes=10)
    )
    return {
        "status": "success",
        "message": "Reset token generated",
        "reset_token": reset_token
    }
    
@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    try:
        payload = jwt.decode(data.reset_token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")

        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = await get_users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        hashed_pwd = hash_password(data.new_password)
        await get_users_collection.update_one(
            {"email": email},
            {"$set": {"password": hashed_pwd}}
        )

        return {"status": "success", "message": "Password reset successfully"}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")


