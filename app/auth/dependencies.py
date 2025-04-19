from fastapi import Header, HTTPException, status
from jose import JWTError, jwt
from app.config import SECRET_KEY
from app.db.mongo import users_collection

ALGORITHM = "HS256"

async def get_current_user(authorization: str = Header(...)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    if not authorization.startswith("Bearer "):
        raise credentials_exception

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        user = await users_collection.find_one({"email": email})
        if not user:
            raise credentials_exception

        return user
    except JWTError:
        raise credentials_exception

