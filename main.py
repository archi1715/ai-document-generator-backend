from fastapi import FastAPI
from app.routes import doc           # ⬅️ Document-related endpoints
from app.auth import routes as auth  # ⬅️ Auth-related endpoints (login/register)

app = FastAPI()

# Register document routes
app.include_router(doc.router)

# Register authentication routes
app.include_router(auth.router)

