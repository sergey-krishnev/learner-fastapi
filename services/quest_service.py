# services/quest_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.quest_repo import quest_repo
from schemas.quest import QuestCreate
from models.models import Quest
from services.exceptions import NotFoundError


class QuestService:
    async def find_all(self, db: AsyncSession):
        return await quest_repo.find_all(db)

    async def find_by_id(self, id: int, db: AsyncSession):
        return await quest_repo.find_by_id(db, id)

    async def save(self, db: AsyncSession, payload: QuestCreate) -> Quest:
        obj = Quest(**payload.model_dump())
        await quest_repo.save(db, obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete_by_id(self, db: AsyncSession, id_: int) -> None:
        deleted = await quest_repo.delete_by_id(db, id_)
        if not deleted:
            raise NotFoundError(f"Position not found with id: {id_}")
        await db.commit()


quest_service = QuestService()
