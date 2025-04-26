from fastapi import FastAPI
from app.routes import doc, profile
from app.auth import routes as auth
from fastapi.responses import RedirectResponse
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.auth import routes  # 🔄 simple import
from app.routes import subscriber, contact, feedback  # Public APIs

from app.db.mongo import initialize_db
import uvicorn
import logging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI()

# Routes
app.include_router(doc.router)
app.include_router(auth.router)
app.include_router(profile.router)

# 🔐 Register/Login/Change Password
app.include_router(routes.router)  

# ✉️ Subscribe
app.include_router(subscriber.router) 

# 📩 Contact Us
app.include_router(contact.router)

# 💬 Feedback
app.include_router(feedback.router)          

# Add security scheme to OpenAPI docs
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API with JWT Auth",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-documentgenerator.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Hook
@app.on_event("startup")
async def startup_event():
    await initialize_db()

# Root Redirect
@app.get("/")
def root():
    return RedirectResponse(url="/docs")
app.include_router(doc.router)
app.include_router(profile.router)

# For running locally
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
