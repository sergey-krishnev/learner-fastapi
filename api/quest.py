from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.mongo import get_mongo_db
from db.session import get_session
from schemas.quest import QuestOut, QuestCreate, QuestDetailedOut
from services.quest_service import quest_service
from services.exceptions import NotFoundError

router = APIRouter(prefix="/quests", tags=["quests"])


@router.get("", response_model=List[QuestOut])
async def get_all(db: AsyncSession = Depends(get_session)):
    return await quest_service.find_all(db)

@router.get("/{id}", response_model=QuestDetailedOut)
async def get_one(id: int, db: AsyncSession = Depends(get_session), mongo_db = Depends(get_mongo_db)):
    # 1) SQL
    quest = await quest_service.find_by_id(id, db)
    if not quest:
        raise HTTPException(status_code=404, detail=f"Quest not found with id: {id}")
    # 2) Mongo
    col = mongo_db['quest_meta']
    doc = await col.find_one({"quest_id": id}, {"_id": 0})
    scenario = (doc or {}).get("scenario")

    # 3) Склейка в QuestDetailedOut
    base = QuestOut.model_validate(quest)
    return QuestDetailedOut(**base.model_dump(), scenario=scenario)

@router.post("", response_model=QuestOut, status_code=status.HTTP_201_CREATED)
async def create(quest: QuestCreate, db: AsyncSession = Depends(get_session)):
    return await quest_service.save(db, quest)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    try:
        await quest_service.delete_by_id(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None
