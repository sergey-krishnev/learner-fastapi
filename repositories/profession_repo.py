# repositories/profession_repo.py
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.models import Profession

class ProfessionRepository:
    async def find_all(self, db: AsyncSession) -> Sequence[Profession]:
        res = await db.execute(select(Profession).order_by(Profession.id))
        return res.scalars().all()

    async def find_by_id(self, db: AsyncSession, id_: int) -> Optional[Profession]:
        res = await db.execute(select(Profession).where(Profession.id == id_))
        return res.scalar_one_or_none()

    async def save(self, db: AsyncSession, obj: Profession) -> Profession:
        if obj.id is None:
            # Новая запись
            db.add(obj)
            await db.flush()  # получим сгенерированный PK
            return obj
        else:
            # Обновление существующей (upsert по PK)
            persisted = await db.merge(obj)  # ВАЖНО: используйте возвращённый инстанс
            await db.flush()
            return persisted

    async def delete_by_id(self, db: AsyncSession, id_: int) -> int:
        res = await db.execute(delete(Profession).where(Profession.id == id_))
        return int(res.rowcount or 0)

profession_repo = ProfessionRepository()
