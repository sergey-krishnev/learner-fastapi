from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from schemas.skill import SkillOut, SkillCreate, SkillUpdate
from schemas.theory import TheoryOut, TheoryCreate
from services.skill_service import skill_service
from services.exceptions import NotFoundError

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=List[SkillOut])
async def find_all(db: AsyncSession = Depends(get_session)):
    return await skill_service.find_all(db)


@router.put("/{id}", response_model=SkillOut)
async def update(
    id: int,
    skill: SkillUpdate,
    db: AsyncSession = Depends(get_session),
):
    try:
        return await skill_service.update(db, id, skill)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{skill_id}/theories", response_model=List[TheoryOut])
async def get_theories_by_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_session),
):
    try:
        return await skill_service.get_theories_by_skill(db, skill_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{skill_id}/theories", response_model=TheoryOut, status_code=status.HTTP_201_CREATED)
async def add_new_theory_to_skill(
    skill_id: int,
    theory: TheoryCreate,
    db: AsyncSession = Depends(get_session),
):
    try:
        return await skill_service.add_new_theory_to_skill(db, skill_id, theory)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{skill_id}/theories/move-theory", status_code=status.HTTP_204_NO_CONTENT)
async def move_theory(
    skill_id: int,
    target_theory_id: int = Query(..., alias="targetTheoryId"),
    new_index_position: int = Query(..., alias="newIndexPosition"),
    new_parent_id: Optional[int] = Query(None, alias="newParentId"),
    db: AsyncSession = Depends(get_session),
):
    """
    Переместить теорию внутри навыка:
    - targetTheoryId: какую теорию двигаем
    - newIndexPosition: новый order_index
    - newParentId: новый parent_id (может быть null)
    """
    try:
        await skill_service.move_theory(
            db=db,
            skill_id=skill_id,
            target_theory_id=target_theory_id,
            new_index_position=new_index_position,
            new_parent_id=new_parent_id,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None


@router.post("", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
async def save(skill: SkillCreate, db: AsyncSession = Depends(get_session)):
    return await skill_service.save(db, skill)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    try:
        await skill_service.delete_by_id(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None
