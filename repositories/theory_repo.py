from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.models import Theory

class TheoryRepository:
    async def find_all(self, db: AsyncSession) -> Sequence[Theory]:
        res = await db.execute(select(Theory).order_by(Theory.id))
        return res.scalars().all()

    async def find_by_id(self, db: AsyncSession, id_: int) -> Optional[Theory]:
        res = await db.execute(select(Theory).where(Theory.id == id_))
        return res.scalar_one_or_none()

    async def save(self, db: AsyncSession, obj: Theory) -> Theory:
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def exists_by_id(self, db: AsyncSession, id_: int) -> bool:
        return (await self.find_by_id(db, id_)) is not None

    async def delete_by_id(self, db: AsyncSession, id_: int) -> int:
        res = await db.execute(delete(Theory).where(Theory.id == id_))
        return res.rowcount or 0

theory_repo = TheoryRepository()
