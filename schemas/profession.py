# schemas/profession.py
from typing import Optional
from pydantic import BaseModel, Field


class ProfessionBase(BaseModel):
    name: str = Field(..., min_length=1)
    icon: str = Field(..., min_length=1)


class ProfessionCreate(ProfessionBase):
    id: Optional[int] = None


class ProfessionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    icon: Optional[str] = Field(None, min_length=1)


class ProfessionOut(ProfessionBase):
    id: int

    class Config:
        from_attributes = True  # pydantic v2: ORM mode
