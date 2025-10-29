from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import remedy_log, creditors, affidavit, user_profile, monthly_bills, fdcpa_violations, notices, statutes, dispatch, intelligence

app = FastAPI(
    title="Sovereign Financial Navigator API",
    description="API for managing sovereign remedy processes.",
    version="1.0.0",
)

# --- CORS Middleware ---
origins = ["*"]  # Allow all for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"]
    allow_headers=["*"]
)

# --- API Routers ---
app.include_router(remedy_log.router, prefix="/api")
app.include_router(creditors.router, prefix="/api")
app.include_router(affidavit.router, prefix="/api")
app.include_router(user_profile.router, prefix="/api")
app.include_router(monthly_bills.router, prefix="/api")
app.include_router(fdcpa_violations.router, prefix="/api")
app.include_router(notices.router, prefix="/api")
app.include_router(statutes.router, prefix="/api")
app.include_router(dispatch.router, prefix="/api")
app.include_router(intelligence.router, prefix="/api")

@app.get("/")
def read_root():
    """Root endpoint for basic API health check."""
    return {"status": "API is running"}
