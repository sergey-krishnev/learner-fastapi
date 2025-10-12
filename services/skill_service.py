# services/skill_service.py
from __future__ import annotations

from typing import List, Optional, Dict

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.skill_repo import skill_repo
from repositories.theory_repo import theory_repo
from schemas.skill import SkillCreate, SkillUpdate
from schemas.theory import TheoryCreate, TheoryOut
from models.models import Skill, Theory
from services.exceptions import NotFoundError


class SkillService:
    # -------- BASIC CRUD --------

    async def find_all(self, db: AsyncSession) -> List[Skill]:
        return await skill_repo.find_all(db)

    async def save(self, db: AsyncSession, payload: SkillCreate) -> Skill:
        obj = Skill(**payload.model_dump())
        await skill_repo.save(db, obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, id_: int, payload: SkillUpdate) -> Skill:
        existing = await skill_repo.find_by_id(db, id_)
        if not existing:
            raise NotFoundError("Skill not found")

        data = payload.model_dump(exclude_unset=True)
        for field in ("name", "icon"):
            if field in data:
                setattr(existing, field, data[field])

        await skill_repo.save(db, existing)
        await db.commit()
        await db.refresh(existing)
        return existing

    async def delete_by_id(self, db: AsyncSession, id_: int) -> None:
        deleted = await skill_repo.delete_by_id(db, id_)
        if not deleted:
            raise NotFoundError(f"Position not found with id: {id_}")
        await db.commit()

    # -------- QUERIES / BUSINESS --------

    async def get_theories_by_skill(self, db: AsyncSession, skill_id: int) -> List[TheoryOut]:

        def _to_out(obj: Theory) -> TheoryOut:
            """Быстрая проекция ORM -> DTO без доступа к отношениям (только столбцы)."""
            return TheoryOut(
                id=obj.id,
                title=obj.title,
                content=obj.content,
                difficultyLevel=obj.difficulty_level,
                orderIndex=obj.order_index,
                skill_id=obj.skill_id,
                parent_id=obj.parent_id,
                subTheories=[],
            )

        if not await skill_repo.find_by_id(db, skill_id):
            raise NotFoundError("Skill not found")

        # 1) Берём корни (parent_id IS NULL) отсортированные по order_index
        res_roots = await db.scalars(
            select(Theory)
            .where(and_(Theory.skill_id == skill_id, Theory.parent_id.is_(None)))
            .order_by(Theory.order_index)
        )
        root_orms: List[Theory] = res_roots.all()
        if not root_orms:
            return []

        # DTO для корней
        roots: List[TheoryOut] = [_to_out(o) for o in root_orms]

        # Индекс: id -> DTO (чтобы быстро подвешивать детей к родителю)
        dto_index: Dict[int, TheoryOut] = {dto.id: dto for dto in roots}

        # Текущая «граница» — id узлов, для которых ищем детей
        frontier_ids: List[int] = [dto.id for dto in roots]

        # 2) Идём уровнями вниз, пока есть дети
        while frontier_ids:
            res_children = await db.scalars(
                select(Theory)
                .where(Theory.parent_id.in_(frontier_ids))
                .order_by(Theory.order_index)
            )
            children_orms: List[Theory] = res_children.all()
            if not children_orms:
                break  # дальше детей нет — все sub_theories уже []

            next_frontier: List[int] = []

            for child in children_orms:
                child_dto = _to_out(child)
                # Подвешиваем к родителю (он уже есть в индексе)
                parent_dto = dto_index.get(child.parent_id)
                if parent_dto is not None:
                    parent_dto.subTheories.append(child_dto)
                # Регистрируем текущего ребёнка как потенциального родителя следующего уровня
                dto_index[child_dto.id] = child_dto
                next_frontier.append(child_dto.id)

            frontier_ids = next_frontier

        # На этом этапе у всех листьев sub_theories == []
        return roots

    async def add_new_theory_to_skill(self, db: AsyncSession, skill_id: int, payload: TheoryCreate) -> Theory:
        # (1) Найти скилл
        skill = await skill_repo.find_by_id(db, skill_id)
        if not skill:
            raise NotFoundError("Skill not found")

        data = payload.model_dump(exclude_unset=True)
        parent_id: Optional[int] = data.get("parent")

        # (2) Вычислить новый order_index среди «соседей»
        if parent_id is not None:
            # проверим, что родитель существует и принадлежит этому же скиллу
            parent = await theory_repo.find_by_id(db, parent_id)
            if not parent:
                raise NotFoundError("Parent theory not found")
            if parent.skill_id != skill_id:
                raise RuntimeError("Parent theory belongs to another skill")

            max_idx = await self._max_order_index_among_children(db, parent_id)
            next_index = (max_idx or 0) + 1
        else:
            max_idx = await self._max_order_index_among_root_theories(db, skill_id)
            next_index = (max_idx or 0) + 1

        # (3) Создать Theory и задать поля
        new_theory = Theory()
        new_theory.title = data.get("title")
        new_theory.content = data.get("content")
        new_theory.skill_id = skill_id
        new_theory.parent_id = parent_id
        new_theory.order_index = next_index

        # (4) Рекурсивно проставить поля для поддерева, если оно пришло (на случай расширенного запроса)
        # В нашей базовой схеме TheoryCreate не содержит sub_theories, но этот код оставлен на будущее.
        if getattr(new_theory, "sub_theories", None):
            self._set_parent_and_skill_in_subtheories(new_theory, skill_id)

        await theory_repo.save(db, new_theory)
        await db.commit()
        await db.refresh(new_theory)
        return new_theory

    async def move_theory(
        self,
        db: AsyncSession,
        skill_id: int,
        target_theory_id: int,
        new_index_position: int,
        new_parent_id: Optional[int],
    ) -> None:
        # 1) Найти перемещаемую теорию
        target = await theory_repo.find_by_id(db, target_theory_id)
        if not target:
            raise NotFoundError("Target theory not found")
        if target.skill_id != skill_id:
            raise RuntimeError("Target theory belongs to another skill")

        # 2) Найти нового родителя (если указан)
        new_parent: Optional[Theory] = None
        if new_parent_id is not None:
            new_parent = await theory_repo.find_by_id(db, new_parent_id)
            if not new_parent:
                raise NotFoundError("Parent theory not found")
            if new_parent.skill_id != skill_id:
                raise RuntimeError("Parent theory belongs to another skill")

        # 3) Получить список «детей» для нового родителя (или корневой список)
        if new_parent is not None:
            children = await self._get_children_of_parent(db, new_parent.id)
        else:
            children = await self._get_theories_by_skill(db, skill_id)  # корневые

        # 4) Обновить у target теории parent_id и временно order_index
        target.parent_id = new_parent.id if new_parent else None
        target.order_index = int(new_index_position)
        await theory_repo.save(db, target)
        await db.flush()

        # 5) Пересобрать порядок: исключаем target из текущего children списка и вставляем на новую позицию
        children_wo_target = [t for t in children if t.id != target_theory_id]
        # границы позиции
        pos = max(0, min(int(new_index_position), len(children_wo_target)))
        children_reordered = list(children_wo_target)
        children_reordered.insert(pos, target)

        # 6) Пронумеровать 0..N-1 и закоммитить
        for i, t in enumerate(children_reordered):
            # обновляем in-memory и БД
            t.order_index = i

        # Эффективная массовая запись — единым UPDATE (опционально):
        for t in children_reordered:
            await db.execute(
                update(Theory)
                .where(Theory.id == t.id)
                .values(order_index=t.order_index, parent_id=t.parent_id)
            )

        await db.commit()

    # -------- Helpers --------

    async def _max_order_index_among_children(self, db: AsyncSession, parent_id: int) -> Optional[int]:
        res = await db.execute(
            select(Theory.order_index)
            .where(Theory.parent_id == parent_id)
            .order_by(Theory.order_index.desc())
            .limit(1)
        )
        return res.scalar_one_or_none()

    async def _max_order_index_among_root_theories(self, db: AsyncSession, skill_id: int) -> Optional[int]:
        res = await db.execute(
            select(Theory.order_index)
            .where(and_(Theory.skill_id == skill_id, Theory.parent_id.is_(None)))
            .order_by(Theory.order_index.desc())
            .limit(1)
        )
        return res.scalar_one_or_none()

    async def _get_children_of_parent(self, db: AsyncSession, parent_id: int) -> List[Theory]:
        res = await db.execute(
            select(Theory)
            .where(Theory.parent_id == parent_id)
            .order_by(Theory.order_index)
        )
        return list(res.scalars())

    async def _get_theories_by_skill(self, db: AsyncSession, skill_id: int) -> List[Theory]:
        res_roots = await db.scalars(
            select(Theory)
            .where(and_(Theory.skill_id == skill_id, Theory.parent_id.is_(None)))
            .order_by(Theory.order_index)
        )
        return list(res_roots)

    def _set_parent_and_skill_in_subtheories(self, parent: Theory, skill_id: int) -> None:
        """
        Рекурсивно проставляет parent/skill/order_index детям.
        Стартовый parent уже проставлен снаружи, порядок детей — 0..N-1.
        """
        subs = getattr(parent, "sub_theories", None) or []
        for idx, st in enumerate(subs):
            st.parent = parent
            st.skill_id = skill_id
            st.order_index = idx
            self._set_parent_and_skill_in_subtheories(st, skill_id)


skill_service = SkillService()
