# from fastapi import FastAPI
# from app.routes import doc           # ⬅️ Document-related endpoints
# from app.auth import auth, routes as auth  # ⬅️ Auth-related endpoints (login/register)
# from app.routes import doc, profile
# from fastapi.responses import RedirectResponse
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.openapi.utils import get_openapi


# app = FastAPI()

# # Register document routes
# app.include_router(doc.router)

# # Register authentication routes
# app.include_router(auth.router)

# # profile routes
# app.include_router(profile.router)

# # Add security scheme to OpenAPI docs
# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="Your API",
#         version="1.0.0",
#         description="API with JWT Auth",
#         routes=app.routes,
#     )
#     openapi_schema["components"]["securitySchemes"] = {
#         "BearerAuth": {
#             "type": "http",
#             "scheme": "bearer",
#             "bearerFormat": "JWT",
#         }
#     }
#     # Apply globally (optional: or add per-route)
#     for path in openapi_schema["paths"].values():
#         for operation in path.values():
#             operation["security"] = [{"BearerAuth": []}]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi

# # Redirect root to Swagger docs
# @app.get("/")
# def root():
#     return RedirectResponse(url="/docs")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Replace with specific domains in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )




# File: main.py
from fastapi import FastAPI, HTTPException
from app.routes import doc, profile
from app.auth import routes as auth_routes
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.db.mongo import initialize_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("main")

app = FastAPI()

# Register routes
app.include_router(doc.router)
app.include_router(auth_routes.router)
app.include_router(profile.router)

# Initialize database on startup
@app.on_event("startup")
async def startup_db_client():
    logger.info("Starting application and connecting to database...")
    result = await initialize_db()
    if result:
        logger.info("Database initialization successful")
    else:
        logger.warning("Database initialization failed, application will use fallback mode")

# Add exception handler for uncaught exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    error_msg = f"Uncaught exception: {str(exc)}"
    logger.error(error_msg)
    return {"status": "error", "message": "An internal server error occurred"}, 500

# Add security scheme to OpenAPI docs
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AI Document Generator API",
        version="1.0.0",
        description="API with JWT Authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Apply security requirements to routes
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Redirect root to Swagger docs
@app.get("/")
def root():
    return RedirectResponse(url="/docs")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)