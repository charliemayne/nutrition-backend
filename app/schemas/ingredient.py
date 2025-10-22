from pydantic import BaseModel, Field
from typing import List, Dict, Tuple, Optional, Union

class IngredientSchema(BaseModel):
    """Schema for ingredient data"""
    id: Optional[int] = None
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    calories_per_unit: Optional[float] = None
    protein_per_unit: Optional[float] = None

    class Config:
        from_attributes = True


class GroceryListItem(BaseModel):
    """Individual item in the grocery list with aggregated quantities"""
    ingredient_name: str
    total_quantity: float
    unit: str
    category: Optional[str] = None
    recipes_used_in: List[str] = Field(default_factory=list)
    already_owned: bool = Field(default=False, description="Whether the user already owns this ingredient")
