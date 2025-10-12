from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.models import UserProgress


class UserProgressRepository:
    async def find_all(self, db: AsyncSession) -> Sequence[UserProgress]:
        res = await db.execute(select(UserProgress).order_by(UserProgress.id))
        return res.scalars().all()

    async def find_by_id(self, db: AsyncSession, id_: int) -> Optional[UserProgress]:
        res = await db.execute(select(UserProgress).where(UserProgress.id == id_))
        return res.scalar_one_or_none()

    async def save(self, db: AsyncSession, obj: UserProgress) -> UserProgress:
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def delete_by_id(self, db: AsyncSession, id_: int) -> int:
        res = await db.execute(delete(UserProgress).where(UserProgress.id == id_))
        return int(res.rowcount or 0)


user_progress_repo = UserProgressRepository()
