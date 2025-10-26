from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import meta, analyze, guide

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="An API for analyzing and guiding essay writing"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta.router)
app.include_router(analyze.router)
app.include_router(guide.router)