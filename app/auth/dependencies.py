from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import SECRET_KEY
from app.db.mongo import users_collection

# Define the OAuth2 flow using /auth/login as token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT algorithm used
ALGORITHM = "HS256"

# Function to decode JWT and fetch current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        print("🔐 Token received:", token)  # 🐞 DEBUG LINE

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        print("📧 Email from token:", email)  # 🐞 DEBUG LINE

        if email is None:
            raise credentials_exception

        user = await users_collection.find_one({"email": email})
        print("👤 User found:", user)  # 🐞 DEBUG LINE

        if user is None:
            raise credentials_exception

        return user

    except JWTError as e:
        print("❌ JWT decode error:", e)  # 🐞 DEBUG LINE
        raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception


