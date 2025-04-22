from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.config import SECRET_KEY

# SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Required fields for token
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),         # issued at
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# File: app/auth/auth.py
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from app.config import SECRET_KEY

# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60

# from jose import jwt
# import os

# # Configure password context and JWT settings
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Get these from environment variables in production
# SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-development-only")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# def hash_password(password: str) -> str:
#     """Hash a password for storing."""
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify a stored password against the provided password."""
#     return pwd_context.verify(plain_password, hashed_password)


# def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + expires_delta
#     to_encode.update({"exp": expire})  # expiration added
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
# def create_access_token(data: dict, expires_delta: timedelta = None):
#     """Create a new JWT token."""
#     to_encode = data.copy()
    
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
#     return encoded_jwt
