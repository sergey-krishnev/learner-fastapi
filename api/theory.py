from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from schemas.theory import TheoryOut, TheoryCreate, TheoryUpdate
from services.theory_service import theory_service
from services.exceptions import NotFoundError

router = APIRouter(prefix="/theories", tags=["theories"])

@router.get("", response_model=List[TheoryOut])
async def get_all(db: AsyncSession = Depends(get_session)):
    return await theory_service.find_all(db)

@router.post("", response_model=TheoryOut, status_code=status.HTTP_201_CREATED)
async def create(theory: TheoryCreate, db: AsyncSession = Depends(get_session)):
    return await theory_service.save(db, theory)

@router.put("/{id}", response_model=TheoryOut)
async def update(id: int, theory: TheoryUpdate, db: AsyncSession = Depends(get_session)):
    try:
        return await theory_service.update(db, id, theory)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_session)):
    try:
        await theory_service.delete_by_id(db, id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None
