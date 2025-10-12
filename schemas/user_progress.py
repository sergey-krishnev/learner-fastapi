from typing import List
from pydantic import BaseModel, field_serializer, Field


class UserProgressOut(BaseModel):
    id: int
    user_name: str = Field(serialization_alias="userName")
    total_experience_points: int = Field(serialization_alias="totalExperiencePoints")
    total_gold_points: int = Field(serialization_alias="totalGoldPoints")

    completed_theories: List[int] = Field(default_factory=list, serialization_alias="completedTheories")
    completed_quests: List[int] = Field(default_factory=list, serialization_alias="completedQuests")
    selected_professions: List[int] = Field(default_factory=list, serialization_alias="selectedProfessions")

    class Config:
        from_attributes = True  # ORM mode (Pydantic v2)

    # --- сериализаторы: ORM-объекты -> списки id ---

    @field_serializer("completed_theories")
    def _ser_completed_theories(self, value):
        # value приходит как list[Theory] из ORM; вернём list[int]
        return [t.id for t in (value or [])]

    @field_serializer("completed_quests")
    def _ser_completed_quests(self, value):
        # value: list[Quest] -> list[int]
        return [q.id for q in (value or [])]

    @field_serializer("selected_professions")
    def _ser_selected_professions(self, value):
        # value: list[Profession] -> list[int]
        return [p.id for p in (value or [])]
