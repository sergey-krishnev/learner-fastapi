# schemas/quest.py
from typing import Optional
from pydantic import BaseModel

class QuestBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    reward_points: int = 0
    reading_points: int = 0
    listening_points: int = 0
    speaking_points: int = 0
    writing_points: int = 0

class QuestCreate(QuestBase):
    pass

class QuestOut(QuestBase):
    id: int
    class Config:
        from_attributes = True
