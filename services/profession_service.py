# services/profession_service.py
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from repositories.profession_repo import profession_repo
from repositories.skill_repo import skill_repo
from schemas.profession import ProfessionCreate
from schemas.skill import SkillCreate
from models.models import Profession, Skill
from services.exceptions import NotFoundError


class ProfessionService:
    async def find_all(self, db: AsyncSession) -> List[Profession]:
        return await profession_repo.find_all(db)

    async def get_skills_by_profession(self, db: AsyncSession, profession_id: int) -> List[Skill]:
        # Явно загружаем skills (в async-режиме избегаем ленивой загрузки)
        res = await db.execute(
            select(Profession)
            .options(selectinload(Profession.skills))
            .where(Profession.id == profession_id)
        )
        profession = res.scalar_one_or_none()
        if not profession:
            raise NotFoundError("Profession not found")
        return profession.skills

    async def add_new_skill_to_profession(
        self, db: AsyncSession, profession_id: int, payload: SkillCreate
    ) -> Skill:
        # Найдём профессию
        res = await db.execute(
            select(Profession)
            .options(selectinload(Profession.skills))
            .where(Profession.id == profession_id)
        )
        profession = res.scalar_one_or_none()
        if not profession:
            raise NotFoundError("Profession not found")

        # Создаём новый Skill и устанавливаем двустороннюю связь
        skill = Skill(**payload.model_dump())
        # Достаточно добавить в одну сторону — back_populates сделает зеркально
        profession.skills.append(skill)

        # Сохраняем
        await skill_repo.save(db, skill)
        await db.commit()
        # обновим объект перед возвратом
        await db.refresh(skill)
        return skill

    async def add_existed_skill_to_profession(
        self, db: AsyncSession, profession_id: int, skill_id: int
    ) -> Skill:
        # Профессию грузим со скиллами
        res = await db.execute(
            select(Profession)
            .options(selectinload(Profession.skills))
            .where(Profession.id == profession_id)
        )
        profession = res.scalar_one_or_none()
        if not profession:
            raise NotFoundError(f"Profession with ID {profession_id} not found")

        # Ищем скилл
        skill = await skill_repo.find_by_id(db, skill_id)
        if not skill:
            raise NotFoundError(f"Skill with ID {skill_id} not found")

        # Проверим, не привязан ли уже
        if any(s.id == skill_id for s in profession.skills):
            raise RuntimeError(
                f"Skill with ID {skill_id} already exists in Profession with ID {profession_id}"
            )

        profession.skills.append(skill)
        # Сохраняем именно профессию — хватит, т.к. это M2M через secondary
        await profession_repo.save(db, profession)
        await db.commit()
        await db.refresh(skill)
        return skill

    async def delete_skill_from_profession(
        self, db: AsyncSession, profession_id: int, skill_id: int
    ) -> None:
        # Загрузим профессию с её скиллами
        res_prof = await db.execute(
            select(Profession)
            .options(selectinload(Profession.skills))
            .where(Profession.id == profession_id)
        )
        profession = res_prof.scalar_one_or_none()
        if not profession:
            raise NotFoundError("Profession not found")

        # Загрузим скилл с его профессиями (чтобы понять, остались ли связи)
        res_skill = await db.execute(
            select(Skill)
            .options(selectinload(Skill.professions))
            .where(Skill.id == skill_id)
        )
        skill = res_skill.scalar_one_or_none()
        if not skill:
            raise NotFoundError("Skill not found")

        # Удалим связь
        try:
            profession.skills.remove(skill)
        except ValueError:
            # skill не был привязан к profession
            raise RuntimeError("Skill not found in the profession")

        # Синхронизируем изменения с БД
        await db.flush()

        # Если у skill больше нет профессий — удаляем сам skill (как в Java-коде)
        if not skill.professions or len(skill.professions) == 0:
            await skill_repo.delete(db, skill)

        await db.commit()

    async def save(self, db: AsyncSession, payload: ProfessionCreate) -> Profession:
        obj = Profession(**payload.model_dump())
        await profession_repo.save(db, obj)
        await db.commit()
        return obj

    async def delete_by_id(self, db: AsyncSession, id_: int) -> None:
        deleted = await profession_repo.delete_by_id(db, id_)
        if not deleted:
            raise NotFoundError(f"Position not found with id: {id_}")
        await db.commit()


profession_service = ProfessionService()
