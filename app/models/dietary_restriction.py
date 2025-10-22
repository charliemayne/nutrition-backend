from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


# Association table for many-to-many relationship between recipes and dietary restrictions
recipe_dietary_restrictions = Table(
    "recipe_dietary_restrictions",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
    Column("dietary_restriction_id", Integer, ForeignKey("dietary_restrictions.id")),
)


class DietaryRestriction(Base):
    __tablename__ = "dietary_restrictions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # e.g., "vegan", "gluten-free", "dairy-free"
    description = Column(String, nullable=True)

    def __repr__(self):
        return f"<DietaryRestriction(name='{self.name}')>"
