from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """Natural language query from the user"""
    query: str = Field(..., description="Natural language query describing meals, restrictions, and owned ingredients")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "I want to make 3 dinners this week. I'm vegetarian and already have rice, beans, and onions."
            }
        }


class ParsedQuery(BaseModel):
    """Structured data extracted from natural language query"""
    dietary_restrictions: List[str] = Field(default_factory=list, description="List of dietary restrictions (e.g., 'vegan', 'gluten-free')")
    meal_types: List[str] = Field(default_factory=list, description="Types of meals requested (e.g., 'breakfast', 'lunch', 'dinner')")
    meal_count: Optional[int] = Field(None, description="Number of meals requested")
    owned_ingredients: List[str] = Field(default_factory=list, description="Ingredients the user already has")
    required_ingredients: List[str] = Field(default_factory=list, description="Ingredients that must be in the recipe (e.g., 'ground beef', 'chicken')")
    cuisine_preferences: List[str] = Field(default_factory=list, description="Preferred cuisines (e.g., 'Italian', 'Mexican')")
    protein_requirement: Optional[int] = Field(None, description="Minimum protein in grams per serving")
    other_requirements: Optional[str] = Field(None, description="Any other requirements or preferences")


class QueryResponse(BaseModel):
    """Response containing parsed query, suggested recipes, and grocery list"""
    parsed_query: ParsedQuery
    suggested_recipes: List[dict]  # Will contain RecipeSchema objects
    grocery_list: List[dict]  # Will contain GroceryListItem objects
    total_estimated_cost: Optional[float] = None  # For future optimization features
    recipes_from_web: int = Field(default=0, description="Number of recipes fetched from the web")
    search_performed: bool = Field(default=False, description="Whether a web search was performed")
