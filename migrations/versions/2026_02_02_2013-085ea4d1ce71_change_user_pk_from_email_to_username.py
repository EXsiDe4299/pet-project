"""change user pk from email to username

Revision ID: 085ea4d1ce71
Revises: 70766bcbede2
Create Date: 2026-02-02 20:13:36.022869

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "085ea4d1ce71"
down_revision: Union[str, None] = "70766bcbede2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        op.f("fk_stories_author_email_users"), "stories", type_="foreignkey"
    )
    op.drop_constraint(op.f("fk_tokens_email_users"), "tokens", type_="foreignkey")
    op.drop_constraint(
        op.f("fk_user_story_association_user_email_users"),
        "user_story_association",
        type_="foreignkey",
    )

    op.drop_constraint(op.f("uq_tokens_email"), "tokens", type_="unique")
    op.drop_constraint(
        op.f("uq_user_story_association_user_email"),
        "user_story_association",
        type_="unique",
    )
    op.drop_constraint(op.f("uq_users_username"), "users", type_="unique")

    op.drop_constraint(op.f("pk_users"), "users", type_="primary")

    op.alter_column(
        "users",
        "username",
        existing_type=sa.VARCHAR(length=20),
        type_=sa.String(length=150),
        existing_nullable=False,
    )

    op.create_primary_key(op.f("pk_users"), "users", ["username"])

    op.add_column(
        "stories", sa.Column("author_username", sa.String(length=150), nullable=False)
    )

    op.create_foreign_key(
        op.f("fk_stories_author_username_users"),
        "stories",
        "users",
        ["author_username"],
        ["username"],
    )

    op.drop_column("stories", "author_email")

    op.add_column(
        "tokens", sa.Column("username", sa.String(length=150), nullable=False)
    )

    op.create_unique_constraint(op.f("uq_tokens_username"), "tokens", ["username"])

    op.create_foreign_key(
        op.f("fk_tokens_username_users"), "tokens", "users", ["username"], ["username"]
    )

    op.drop_column("tokens", "email")

    op.add_column(
        "user_story_association",
        sa.Column("username", sa.String(length=150), nullable=True),
    )

    op.create_unique_constraint(
        op.f("uq_user_story_association_username"),
        "user_story_association",
        ["username", "story_id"],
    )

    op.create_foreign_key(
        op.f("fk_user_story_association_username_users"),
        "user_story_association",
        "users",
        ["username"],
        ["username"],
    )

    op.drop_column("user_story_association", "user_email")

    op.create_unique_constraint(op.f("uq_users_email"), "users", ["email"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_stories_author_username_users"), "stories", type_="foreignkey"
    )
    op.drop_constraint(op.f("fk_tokens_username_users"), "tokens", type_="foreignkey")
    op.drop_constraint(
        op.f("fk_user_story_association_username_users"),
        "user_story_association",
        type_="foreignkey",
    )

    op.drop_constraint(op.f("uq_tokens_username"), "tokens", type_="unique")
    op.drop_constraint(
        op.f("uq_user_story_association_username"),
        "user_story_association",
        type_="unique",
    )
    op.drop_constraint(op.f("uq_users_email"), "users", type_="unique")

    op.drop_constraint(op.f("pk_users"), "users", type_="primary")

    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(length=150),
        type_=sa.VARCHAR(length=20),
        existing_nullable=False,
    )

    op.add_column(
        "stories",
        sa.Column("author_email", sa.VARCHAR(), autoincrement=False, nullable=False),
    )

    op.create_primary_key(op.f("pk_users"), "users", ["email"])

    op.create_foreign_key(
        op.f("fk_stories_author_email_users"),
        "stories",
        "users",
        ["author_email"],
        ["email"],
    )

    op.drop_column("stories", "author_username")

    op.add_column(
        "tokens", sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=False)
    )

    op.create_unique_constraint(
        op.f("uq_tokens_email"),
        "tokens",
        ["email"],
        postgresql_nulls_not_distinct=False,
    )

    op.create_foreign_key(
        op.f("fk_tokens_email_users"), "tokens", "users", ["email"], ["email"]
    )

    op.drop_column("tokens", "username")

    op.add_column(
        "user_story_association",
        sa.Column("user_email", sa.VARCHAR(), autoincrement=False, nullable=True),
    )

    op.create_unique_constraint(
        op.f("uq_user_story_association_user_email"),
        "user_story_association",
        ["user_email", "story_id"],
        postgresql_nulls_not_distinct=False,
    )

    op.create_foreign_key(
        op.f("fk_user_story_association_user_email_users"),
        "user_story_association",
        "users",
        ["user_email"],
        ["email"],
    )

    op.drop_column("user_story_association", "username")
