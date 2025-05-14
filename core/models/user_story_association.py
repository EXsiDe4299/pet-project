from sqlalchemy import ForeignKey, UniqueConstraint, Table, Column

from core.models.base import Base


UserStoryAssociation = Table(
    "user_story_association",
    Base.metadata,
    Column("user_email", ForeignKey("users.email")),
    Column("story_id", ForeignKey("stories.id")),
    UniqueConstraint("user_email", "story_id"),
)
