from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from schemas.profession import ProfessionOut, ProfessionCreate
from schemas.skill import SkillOut, SkillCreate
from services.profession_service import profession_service
from services.exceptions import NotFoundError

router = APIRouter(prefix="/professions", tags=["professions"])


@router.get("", response_model=List[ProfessionOut])
async def get_all(db: AsyncSession = Depends(get_session)):
    return await profession_service.find_all(db)


@router.get("/{id}/skills", response_model=List[SkillOut])
async def get_skills_by_profession(id: int, db: AsyncSession = Depends(get_session)):
    try:
        return await profession_service.get_skills_by_profession(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{id}/skills", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
async def add_new_skill_to_profession(
    id: int,
    skill: SkillCreate,
    db: AsyncSession = Depends(get_session),
):
    try:
        return await profession_service.add_new_skill_to_profession(db, id, skill)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{id}/skills/{skill_id}", response_model=SkillOut)
async def add_existed_skill_to_profession(
    id: int,
    skill_id: int,
    db: AsyncSession = Depends(get_session),
):
    try:
        return await profession_service.add_existed_skill_to_profession(db, id, skill_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=ProfessionOut, status_code=status.HTTP_201_CREATED)
async def create(profession: ProfessionCreate, db: AsyncSession = Depends(get_session)):
    return await profession_service.save(db, profession)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    try:
        await profession_service.delete_by_id(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None


@router.delete("/{id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill_from_profession(
    id: int,
    skill_id: int,
    db: AsyncSession = Depends(get_session),
):
    try:
        await profession_service.delete_skill_from_profession(db, id, skill_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None
