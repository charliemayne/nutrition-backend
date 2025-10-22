from pydantic import BaseModel
from typing import Optional, List


class RecipeIngredientSchema(BaseModel):
    """Schema for recipe ingredients with quantities"""
    ingredient_name: str
    quantity: float
    unit: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class RecipeSchema(BaseModel):
    """Schema for recipe data"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    cuisine: Optional[str] = None
    meal_type: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    servings: int = 4
    ingredients: List[RecipeIngredientSchema] = []
    dietary_restrictions: List[str] = []

    class Config:
        from_attributes = True
