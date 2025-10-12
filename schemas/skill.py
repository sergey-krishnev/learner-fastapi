# schemas/skill.py
from typing import Optional
from pydantic import BaseModel, Field


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1)
    icon: str = Field(..., min_length=1)


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    icon: Optional[str] = Field(None, min_length=1)


class SkillOut(SkillBase):
    id: int

    class Config:
        from_attributes = True
