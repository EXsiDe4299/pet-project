from sqlalchemy import ForeignKey, UniqueConstraint, Table, Column

from core.models.base import Base

UserStoryAssociation = Table(
    "user_story_association",
    Base.metadata,
    Column("username", ForeignKey("users.username")),
    Column("story_id", ForeignKey("stories.id")),
    UniqueConstraint("username", "story_id"),
)
