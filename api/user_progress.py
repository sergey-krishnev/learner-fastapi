from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from schemas.user_progress import UserProgressOut
from services.user_progress_service import user_progress_service
from services.exceptions import NotFoundError

router = APIRouter(prefix="/user-progress", tags=["user-progress"])

class UserNameIn(BaseModel):
    userName: str = Field(..., min_length=1)


@router.get("", response_model=UserProgressOut)
async def get_user_progress(db: AsyncSession = Depends(get_session)):
    try:
        up = await user_progress_service.get_user_progress(db)
        if up is None:
            raise NotFoundError("User progress not found")
        return up
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=UserProgressOut, status_code=status.HTTP_201_CREATED)
async def create_user_progress(payload: UserNameIn, db: AsyncSession = Depends(get_session)):
    return await user_progress_service.create_user_progress(db, payload.userName)
