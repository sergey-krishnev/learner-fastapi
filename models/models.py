# models.py
from __future__ import annotations
from typing import List, Optional

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Table,
    Text,
    CheckConstraint,
    Column
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

# ---------- Base ----------

class Base(DeclarativeBase):
    pass


# ---------- Association Tables (link/junction) ----------
profession_skill = Table(
    "profession_skill",
    Base.metadata,
    Column("skill_id", ForeignKey("skill.id", ondelete="CASCADE"), primary_key=True),
    Column("profession_id", ForeignKey("profession.id", ondelete="CASCADE"), primary_key=True),
)

theory_quest = Table(
    "theory_quest",
    Base.metadata,
    Column("theory_id", ForeignKey("theory.id", ondelete="CASCADE"), primary_key=True),
    Column("quest_id", ForeignKey("quest.id", ondelete="CASCADE"), primary_key=True),
)

user_completed_theories = Table(
    "user_completed_theories",
    Base.metadata,
    Column("user_progress_id", ForeignKey("user_progress.id", ondelete="CASCADE"), primary_key=True),
    Column("theory_id", ForeignKey("theory.id", ondelete="CASCADE"), primary_key=True),
)

user_completed_quests = Table(
    "user_completed_quests",
    Base.metadata,
    Column("user_progress_id", ForeignKey("user_progress.id", ondelete="CASCADE"), primary_key=True),
    Column("quest_id", ForeignKey("quest.id", ondelete="CASCADE"), primary_key=True),
)

user_selected_professions = Table(
    "user_selected_professions",
    Base.metadata,
    Column("user_progress_id", ForeignKey("user_progress.id", ondelete="CASCADE"), primary_key=True),
    Column("profession_id", ForeignKey("profession.id", ondelete="CASCADE"), primary_key=True),
)


# -------- Модели (имена как в БД) --------
class Profession(Base):
    __tablename__ = "profession"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str] = mapped_column(String(255), nullable=False)

    skills: Mapped[List["Skill"]] = relationship(
        secondary=profession_skill,
        back_populates="professions",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("name <> ''", name="ck_profession_name_not_blank"),
        CheckConstraint("icon <> ''", name="ck_profession_icon_not_blank"),
    )


class Skill(Base):
    __tablename__ = "skill"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str] = mapped_column(String(255), nullable=False)

    professions: Mapped[List[Profession]] = relationship(
        secondary=profession_skill,
        back_populates="skills",
        lazy="selectin",
    )

    theories: Mapped[List["Theory"]] = relationship(
        back_populates="skill",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("name <> ''", name="ck_skill_name_not_blank"),
        CheckConstraint("icon <> ''", name="ck_skill_icon_not_blank"),
    )


class Theory(Base):
    __tablename__ = "theory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("theory.id", ondelete="SET NULL"))
    parent: Mapped[Optional["Theory"]] = relationship(
        remote_side="Theory.id",
        back_populates="sub_theories",
        lazy="raise",
    )

    sub_theories: Mapped[List["Theory"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Theory.order_index",
    )

    skill_id: Mapped[Optional[int]] = mapped_column(ForeignKey("skill.id", ondelete="SET NULL"))
    skill: Mapped[Optional[Skill]] = relationship(back_populates="theories", lazy="selectin")

    quests: Mapped[List["Quest"]] = relationship(
        secondary=theory_quest,
        back_populates="theories",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("title <> ''", name="ck_theory_title_not_blank"),
        CheckConstraint("content <> ''", name="ck_theory_content_not_blank"),
    )


class Quest(Base):
    __tablename__ = "quest"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    reward_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reading_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    listening_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    speaking_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    writing_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    theories: Mapped[List[Theory]] = relationship(
        secondary=theory_quest,
        back_populates="quests",
        lazy="selectin",
    )

    __table_args__ = (CheckConstraint("title <> ''", name="ck_quest_title_not_blank"),)


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)

    total_experience_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_gold_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    completed_theories: Mapped[List[Theory]] = relationship(
        secondary=user_completed_theories,
        lazy="selectin",
    )
    completed_quests: Mapped[List[Quest]] = relationship(
        secondary=user_completed_quests,
        lazy="selectin",
    )
    selected_professions: Mapped[List[Profession]] = relationship(
        secondary=user_selected_professions,
        lazy="selectin",
    )

    __table_args__ = (CheckConstraint("user_name <> ''", name="ck_userprogress_username_not_blank"),)
