
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME

# Create MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# Optional: Define collection shortcuts for convenience
users_collection = db.get_collection("users")
documents_collection = db.get_collection("documents")



