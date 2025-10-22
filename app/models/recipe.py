from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base
from .dietary_restriction import recipe_dietary_restrictions


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    cuisine = Column(String, nullable=True)  # e.g., "Italian", "Mexican", "Asian"
    meal_type = Column(String, nullable=True)  # e.g., "breakfast", "lunch", "dinner", "snack"
    prep_time_minutes = Column(Integer, nullable=True)
    servings = Column(Integer, default=4)

    # Relationships
    recipe_ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    dietary_restrictions = relationship(
        "DietaryRestriction",
        secondary=recipe_dietary_restrictions,
        backref="recipes"
    )

    def __repr__(self):
        return f"<Recipe(name='{self.name}', meal_type='{self.meal_type}')>"


class RecipeIngredient(Base):
    """Junction table linking recipes to ingredients with quantities"""
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # e.g., "cup", "tbsp", "lb"
    notes = Column(String, nullable=True)  # e.g., "chopped", "diced", "optional"

    # Relationships
    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient")

    def __repr__(self):
        return f"<RecipeIngredient(recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id}, quantity={self.quantity} {self.unit})>"
