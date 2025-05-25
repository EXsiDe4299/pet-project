"""Initial migration

Revision ID: 70766bcbede2
Revises:
Create Date: 2025-05-25 08:28:19.177741

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "70766bcbede2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("username", sa.String(length=20), nullable=False),
        sa.Column("hashed_password", sa.LargeBinary(), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_name", sa.String(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "is_email_verified",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=50), server_default="user", nullable=False),
        sa.Column(
            "registered_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("email", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_table(
        "stories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column(
            "likes_number",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("author_email", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_email"],
            ["users.email"],
            name=op.f("fk_stories_author_email_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stories")),
    )
    op.create_table(
        "tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("email_verification_token", sa.String(), nullable=True),
        sa.Column(
            "email_verification_token_exp",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("forgot_password_token", sa.String(), nullable=True),
        sa.Column(
            "forgot_password_token_exp",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["email"], ["users.email"], name=op.f("fk_tokens_email_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tokens")),
        sa.UniqueConstraint("email", name=op.f("uq_tokens_email")),
    )
    op.create_table(
        "user_story_association",
        sa.Column("user_email", sa.String(), nullable=True),
        sa.Column("story_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["story_id"],
            ["stories.id"],
            name=op.f("fk_user_story_association_story_id_stories"),
        ),
        sa.ForeignKeyConstraint(
            ["user_email"],
            ["users.email"],
            name=op.f("fk_user_story_association_user_email_users"),
        ),
        sa.UniqueConstraint(
            "user_email",
            "story_id",
            name=op.f("uq_user_story_association_user_email"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_story_association")
    op.drop_table("tokens")
    op.drop_table("stories")
    op.drop_table("users")
