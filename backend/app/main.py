from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.database import init_db
from app.api.routes import auth, documents, extracted_documents, insights, dashboard, erp, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup DB initialization
    await init_db()
    yield

app = FastAPI(
    title="IntelliParse API",
    description="AI-Powered Document Intelligence Platform for ERP Systems",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for standard error shape
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "detail": None
            }
        }
    )

# Include API Routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(extracted_documents.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(erp.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "platform": "IntelliParse", "model": settings.GEMINI_MODEL}
