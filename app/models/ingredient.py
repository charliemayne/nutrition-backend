from sqlalchemy import Column, Integer, String, Float
from .base import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, index=True)  # e.g., "produce", "dairy", "meat", "pantry"
    unit = Column(String)  # e.g., "cup", "lb", "oz", "count"

    # Nutritional info (optional, for future features)
    calories_per_unit = Column(Float, nullable=True)
    protein_per_unit = Column(Float, nullable=True)

    def __repr__(self):
        return f"<Ingredient(name='{self.name}', category='{self.category}')>"
