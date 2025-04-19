from fastapi import FastAPI
from app.routes import doc           # ⬅️ Document-related endpoints
from app.auth import auth, routes as auth  # ⬅️ Auth-related endpoints (login/register)
from app.routes import doc, profile
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi


app = FastAPI()

# Register document routes
app.include_router(doc.router)

# Register authentication routes
app.include_router(auth.router)

# profile routes
app.include_router(profile.router)

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
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Apply globally (optional: or add per-route)
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

