# schemas/quest.py
from typing import Optional
from pydantic import BaseModel

class QuestBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    preview: Optional[str] = None

class QuestCreate(QuestBase):
    pass

class QuestOut(QuestBase):
    id: int
    class Config:
        from_attributes = True
