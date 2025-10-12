from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TheoryBase(BaseModel):
    title: str
    content: str
    difficultyLevel: int = 0
    orderIndex: int = 0
    skill_id: Optional[int] = Field(default=None, serialization_alias="skill")
    parent_id: Optional[int] = Field(default=None, serialization_alias="parent")

class TheoryCreate(TheoryBase):
    parent: Optional[int] = Field(default=None)
class TheoryUpdate(TheoryBase): pass

class TheoryOut(TheoryBase):
    id: int
    subTheories: List["TheoryOut"] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

TheoryOut.model_rebuild()