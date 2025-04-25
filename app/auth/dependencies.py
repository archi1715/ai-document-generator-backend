from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import SECRET_KEY
from app.db.mongo import users_collection
from app.db.mongo import get_users_collection 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
ALGORITHM = "HS256"



async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        users_collection = get_users_collection()  # ✅ always use latest reference
        if users_collection is None:
            raise HTTPException(status_code=500, detail="Database not initialized")

        user = await users_collection.find_one({"email": email})
        if not user:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception