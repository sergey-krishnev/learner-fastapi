from fastapi import APIRouter
from . import theory, skill, profession, quest, user_progress

api_router = APIRouter()
api_router.include_router(theory.router)
api_router.include_router(skill.router)
api_router.include_router(profession.router)
# api_router.include_router(quest.router)
api_router.include_router(user_progress.router)
