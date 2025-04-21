
# from motor.motor_asyncio import AsyncIOMotorClient
# from app.config import MONGO_URI, DATABASE_NAME

# # # Create MongoDB client
# client = AsyncIOMotorClient(MONGO_URI)
# db = client[DATABASE_NAME]

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
# db = client[DATABASE_NAME]   

# # Optional: Define collection shortcuts for convenience
# users_collection = db.get_collection("users")
# documents_collection = db.get_collection("documents") 
# user_profiles_collection = db.get_collection("user_profiles") 


# File: app/db/mongo.py
from urllib.parse import quote_plus
from motor.motor_asyncio import AsyncIOMotorClient
import os
import certifi
import logging
import ssl

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.db.mongo")

# Initialize connection variables
client = None
db = None
users_collection = None
documents_collection = None
user_profiles_collection = None
DATABASE_NAME = os.getenv("DATABASE_NAME", "ai-document")

async def connect_to_mongodb():
    global client
    
    try:
        logger.info("Attempting to connect to MongoDB Atlas...")
        
        # Hard-code credentials with proper escaping
        username = quote_plus("darshantrks015")
        password = quote_plus("darshan.trks@015")
        
        # Use MongoDB Atlas SRV connection string format
        srv_uri = f"mongodb+srv://{username}:{password}@cluster0.ywacvyp.mongodb.net/?retryWrites=true&w=majority"
        
        # Create client with standard options - avoid using deprecated ssl_cert_reqs
        client = AsyncIOMotorClient(
            srv_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,  # For development only! More secure options for production
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # Test connection with ping
        await client.admin.command('ping')
        logger.info("🚀 MongoDB Atlas connected successfully!")
        
        return client
        
    except Exception as e:
        logger.error(f"❌ MongoDB Atlas connection error: {e}")
        logger.info("Trying alternative connection method...")
        
        try:
            # Try using the standard direct connection format
            connection_string = f"mongodb://{username}:{password}@ac-sxznnot-shard-00-00.ywacvyp.mongodb.net:27017,ac-sxznnot-shard-00-01.ywacvyp.mongodb.net:27017,ac-sxznnot-shard-00-02.ywacvyp.mongodb.net:27017/admin?ssl=true&replicaSet=atlas-10g9ro-shard-0&authSource=admin"
            
            client = AsyncIOMotorClient(
                connection_string,
                tls=True,                       # Use tls instead of ssl
                tlsAllowInvalidCertificates=True,  # Instead of ssl_cert_reqs
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            await client.admin.command('ping')
            logger.info("🚀 MongoDB connected successfully with alternative method!")
            
            return client
            
        except Exception as e2:
            logger.error(f"❌ Alternative connection also failed: {e2}")
            
            # If both methods fail, try a local MongoDB instance as a fallback
            try:
                logger.warning("Attempting to connect to local MongoDB as fallback...")
                local_client = AsyncIOMotorClient("mongodb://localhost:27017")
                await local_client.admin.command('ping')
                logger.info("Connected to local MongoDB instance")
                return local_client
            except Exception as e3:
                logger.error(f"❌ Local connection failed: {e3}")
                logger.error("All connection attempts failed. Application will run without database.")
                return None

# Setup function to be called at application startup
async def initialize_db():
    global client, db, users_collection, documents_collection, user_profiles_collection
    
    client = await connect_to_mongodb()
    
    if client:
        # Use the specified database name (not 'admin' from the connection string)
        db = client[DATABASE_NAME]
        
        # Explicitly create collections if they don't exist
        if "users" not in await db.list_collection_names():
            await db.create_collection("users")
        if "documents" not in await db.list_collection_names():
            await db.create_collection("documents")
        if "user_profiles" not in await db.list_collection_names():
            await db.create_collection("user_profiles")
            
        # Get references to collections
        users_collection = db.users
        documents_collection = db.documents
        user_profiles_collection = db.user_profiles
        
        # Debug check to ensure collections are non-None
        logger.info(f"users_collection initialized: {users_collection is not None}")
        logger.info(f"documents_collection initialized: {documents_collection is not None}")
        logger.info(f"user_profiles_collection initialized: {user_profiles_collection is not None}")
        
        logger.info(f"Successfully initialized collections in database: {DATABASE_NAME}")
        return True
    else:
        logger.warning("⚠️ WARNING: MongoDB collections not initialized. Application will run but database operations will fail.")
        
        # Create dummy collections that log errors when used but don't crash
        class DummyCollection:
            def __init__(self, name):
                self.name = name
                
            async def find_one(self, *args, **kwargs):
                logger.error(f"Attempted to use {self.name}.find_one() but database is not connected")
                return None
                
            async def insert_one(self, *args, **kwargs):
                logger.error(f"Attempted to use {self.name}.insert_one() but database is not connected")
                return None
                
            async def update_one(self, *args, **kwargs):
                logger.error(f"Attempted to use {self.name}.update_one() but database is not connected")
                return None
                
            async def delete_one(self, *args, **kwargs):
                logger.error(f"Attempted to use {self.name}.delete_one() but database is not connected")
                return None
                
            async def find(self, *args, **kwargs):
                logger.error(f"Attempted to use {self.name}.find() but database is not connected")
                return []
        
        users_collection = DummyCollection("users")
        documents_collection = DummyCollection("documents")
        user_profiles_collection = DummyCollection("user_profiles") 
        return False

# Function to get collection references (helpful for modules imported before DB init)
def get_users_collection():
    return users_collection

def get_documents_collection():
    return documents_collection

def get_user_profiles_collection():
    return user_profiles_collection