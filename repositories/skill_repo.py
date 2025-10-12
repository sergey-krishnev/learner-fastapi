# repositories/skill_repo.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence
from models.models import Skill

class SkillRepository:

    async def find_all(self, db: AsyncSession) -> Sequence[Skill]:
        res = await db.execute(select(Skill).order_by(Skill.id))
        return res.scalars().all()

    async def find_by_id(self, db: AsyncSession, id_: int) -> Optional[Skill]:
        res = await db.execute(select(Skill).where(Skill.id == id_))
        return res.scalar_one_or_none()

    async def save(self, db: AsyncSession, obj: Skill) -> Skill:
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, obj: Skill) -> None:
        await db.delete(obj)

skill_repo = SkillRepository()
