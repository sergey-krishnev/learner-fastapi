# app/services/theory_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.theory_repo import theory_repo
from schemas.theory import TheoryCreate, TheoryUpdate
from models.models import Theory
from services.exceptions import NotFoundError

class TheoryService:
    async def find_all(self, db: AsyncSession):
        return await theory_repo.find_all(db)

    async def save(self, db: AsyncSession, payload: TheoryCreate) -> Theory:
        obj = Theory(**payload.model_dump())
        await theory_repo.save(db, obj)
        await db.commit()
        return obj

    async def delete_by_id(self, db: AsyncSession, id_: int) -> None:
        if not await theory_repo.exists_by_id(db, id_):
            raise NotFoundError(f"Theory not found with id={id_}")
        await theory_repo.delete_by_id(db, id_)
        await db.commit()

    async def update(self, db: AsyncSession, id_: int, payload: TheoryUpdate) -> Theory:
        existing = await theory_repo.find_by_id(db, id_)
        if not existing:
            raise NotFoundError("Theory not found")

        data = payload.model_dump(exclude_unset=True)
        if "title" in data and data["title"] is not None:
            existing.title = data["title"]
        if "content" in data and data["content"] is not None:
            existing.content = data["content"]
        for k in ("difficulty_level", "order_index", "parent_id", "skill_id"):
            if k in data and data[k] is not None:
                setattr(existing, k, data[k])

        await theory_repo.save(db, existing)
        await db.commit()
        return existing

theory_service = TheoryService()
