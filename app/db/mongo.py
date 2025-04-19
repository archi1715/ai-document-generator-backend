
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DATABASE_NAME

# Create MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# Optional: Define collection shortcuts for convenience
users_collection = db.get_collection("users")
documents_collection = db.get_collection("documents")
user_profiles_collection = db.get_collection("user_profiles")


# from urllib.parse import quote_plus
# from motor.motor_asyncio import AsyncIOMotorClient
# from app.config import MONGO_URI, DATABASE_NAME

# # URL-encode the username and password if you have any special characters in them
# username = "darshantrks015"
# password = "darshan.trks@015"

# # URL-encode the username and password
# encoded_username = quote_plus(username)
# encoded_password = quote_plus(password)

# # Update the MONGO_URI with the encoded username and password
# MONGO_URI = MONGO_URI.replace("darshantrks015", encoded_username).replace("darshan.trks@015", encoded_password)

# # Establish the MongoDB connection
# client = AsyncIOMotorClient(MONGO_URI)

# try:
#     # Ping the database to check if it's connected
#     client.admin.command('ping')
#     print("🚀 MongoDB is connected successfully!")
# except Exception as e:
#     print("❌ MongoDB connection error:", e)

# # Define the database and collections
# db = client[DATABASE_NAME]

# users_collection = db.get_collection("users")
# documents_collection = db.get_collection("documents")