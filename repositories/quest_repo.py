# repositories/quest_repo.py
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.models import Quest

class QuestRepository:
    async def find_all(self, db: AsyncSession) -> Sequence[Quest]:
        res = await db.execute(select(Quest).order_by(Quest.id))
        return res.scalars().all()

    async def find_by_id(self, db: AsyncSession, id_: int) -> Optional[Quest]:
        res = await db.execute(select(Quest).where(Quest.id == id_))
        return res.scalar_one_or_none()

    async def save(self, db: AsyncSession, obj: Quest) -> Quest:
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def delete_by_id(self, db: AsyncSession, id_: int) -> int:
        res = await db.execute(delete(Quest).where(Quest.id == id_))
        return int(res.rowcount or 0)

quest_repo = QuestRepository()
