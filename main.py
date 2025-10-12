from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api import api_router

app = FastAPI(title="Education Learner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=settings.cors_allowed_methods,
    allow_headers=settings.cors_allowed_headers,
    allow_credentials=settings.cors_allow_credentials,
    max_age=settings.cors_max_age,
)

app.include_router(api_router, prefix="/api")
