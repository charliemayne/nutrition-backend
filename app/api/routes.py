from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..models.base import get_db
from ..schemas.query import QueryRequest, QueryResponse
from ..schemas.recipe import RecipeSchema
from ..schemas.ingredient import IngredientSchema
from ..services import NLPParser, RecipeMatcher, GroceryListGenerator

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Process a natural language query and return suggested recipes and grocery list.

    This endpoint:
    1. Parses the natural language query
    2. Finds matching recipes
    3. Generates a consolidated grocery list
    4. Removes items the user already owns
    """
    try:
        # Parse the natural language query
        nlp_parser = NLPParser()
        parsed_query = nlp_parser.parse_query(request.query)

        # Find matching recipes
        recipe_matcher = RecipeMatcher(db)
        suggested_recipes = recipe_matcher.find_matching_recipes(parsed_query)

        # Generate grocery list
        grocery_generator = GroceryListGenerator()
        grocery_list = grocery_generator.generate_grocery_list(
            recipes=suggested_recipes,
            owned_ingredients=parsed_query.owned_ingredients
        )

        # Calculate estimated cost (placeholder for now)
        total_cost = grocery_generator.calculate_estimated_cost(grocery_list)

        return QueryResponse(
            parsed_query=parsed_query,
            suggested_recipes=[recipe.model_dump() for recipe in suggested_recipes],
            grocery_list=[item.model_dump() for item in grocery_list],
            total_estimated_cost=total_cost if total_cost > 0 else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/recipes", response_model=List[RecipeSchema])
async def get_all_recipes(db: Session = Depends(get_db)):
    """Get all available recipes"""
    recipe_matcher = RecipeMatcher(db)
    return recipe_matcher.get_all_recipes()


@router.get("/recipes/{recipe_id}", response_model=RecipeSchema)
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get a specific recipe by ID"""
    recipe_matcher = RecipeMatcher(db)
    recipe = recipe_matcher.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "nutrition-backend"}
