# services/user_progress_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_progress_repo import user_progress_repo
from models.models import UserProgress


FIXED_UP_ID = 1


class UserProgressService:
    async def get_user_progress(self, db: AsyncSession) -> UserProgress | None:
        return await user_progress_repo.find_by_id(db, FIXED_UP_ID)

    async def create_user_progress(self, db: AsyncSession, user_name: str) -> UserProgress:
        existing = await user_progress_repo.find_by_id(db, FIXED_UP_ID)
        if existing:
            raise RuntimeError("UserProgress with ID 1 already exists")

        up = UserProgress(id=FIXED_UP_ID, user_name=user_name)
        await user_progress_repo.save(db, up)
        await db.commit()
        await db.refresh(up)
        return up


user_progress_service = UserProgressService()
