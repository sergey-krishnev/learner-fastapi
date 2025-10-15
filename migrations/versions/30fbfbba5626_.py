from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "30fbfbba5626"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "profession",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("icon", sa.String(length=255), nullable=False),
        sa.CheckConstraint("icon <> ''", name="ck_profession_icon_not_blank"),
        sa.CheckConstraint("name <> ''", name="ck_profession_name_not_blank"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "quest",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("preview", sa.String(length=255), nullable=True),
        sa.CheckConstraint("name <> ''", name="ck_quest_name_not_blank"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "skill",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("icon", sa.String(length=255), nullable=False),
        sa.CheckConstraint("icon <> ''", name="ck_skill_icon_not_blank"),
        sa.CheckConstraint("name <> ''", name="ck_skill_name_not_blank"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_name", sa.String(length=255), nullable=False),
        sa.Column("total_experience_points", sa.Integer(), nullable=False),
        sa.Column("total_gold_points", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "user_name <> ''", name="ck_userprogress_username_not_blank"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "profession_skill",
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("profession_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["profession_id"], ["profession.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skill.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("skill_id", "profession_id"),
    )
    op.create_table(
        "theory",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("difficulty_level", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("skill_id", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "content <> ''", name="ck_theory_content_not_blank"
        ),
        sa.CheckConstraint("title <> ''", name="ck_theory_title_not_blank"),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["theory.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skill.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_completed_quests",
        sa.Column("user_progress_id", sa.Integer(), nullable=False),
        sa.Column("quest_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["quest_id"], ["quest.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_progress_id"], ["user_progress.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_progress_id", "quest_id"),
    )
    op.create_table(
        "user_selected_professions",
        sa.Column("user_progress_id", sa.Integer(), nullable=False),
        sa.Column("profession_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["profession_id"], ["profession.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_progress_id"], ["user_progress.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_progress_id", "profession_id"),
    )
    op.create_table(
        "theory_quest",
        sa.Column("theory_id", sa.Integer(), nullable=False),
        sa.Column("quest_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["quest_id"], ["quest.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["theory_id"], ["theory.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("theory_id", "quest_id"),
    )
    op.create_table(
        "user_completed_theories",
        sa.Column("user_progress_id", sa.Integer(), nullable=False),
        sa.Column("theory_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["theory_id"], ["theory.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_progress_id"], ["user_progress.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_progress_id", "theory_id"),
    )


def downgrade() -> None:
    op.drop_table("user_completed_theories")
    op.drop_table("theory_quest")
    op.drop_table("user_selected_professions")
    op.drop_table("user_completed_quests")
    op.drop_table("theory")
    op.drop_table("profession_skill")
    op.drop_table("user_progress")
    op.drop_table("skill")
    op.drop_table("quest")
    op.drop_table("profession")
