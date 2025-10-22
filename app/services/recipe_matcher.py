from typing import List
from sqlalchemy.orm import Session
from ..models import Recipe, DietaryRestriction
from ..schemas.query import ParsedQuery
from ..schemas.recipe import RecipeSchema, RecipeIngredientSchema


class RecipeMatcher:
    """Matches parsed queries to recipes in the database"""

    def __init__(self, db: Session):
        self.db = db

    def find_matching_recipes(self, parsed_query: ParsedQuery) -> List[RecipeSchema]:
        """
        Find recipes that match the parsed query requirements.

        Args:
            parsed_query: Structured query data

        Returns:
            List of matching recipes
        """
        # Start with all recipes
        query = self.db.query(Recipe)

        # Filter by meal type if specified
        if parsed_query.meal_types:
            query = query.filter(Recipe.meal_type.in_(parsed_query.meal_types))

        # Filter by dietary restrictions
        if parsed_query.dietary_restrictions:
            # Get dietary restriction IDs
            restrictions = self.db.query(DietaryRestriction).filter(
                DietaryRestriction.name.in_(parsed_query.dietary_restrictions)
            ).all()

            if restrictions:
                # Recipe must have ALL specified dietary restrictions
                for restriction in restrictions:
                    query = query.filter(Recipe.dietary_restrictions.contains(restriction))

        # Filter by cuisine if specified
        if parsed_query.cuisine_preferences:
            query = query.filter(Recipe.cuisine.in_(parsed_query.cuisine_preferences))

        # Get all matching recipes
        recipes = query.all()

        # Limit results if meal_count is specified
        if parsed_query.meal_count:
            recipes = recipes[:parsed_query.meal_count]

        # Convert to schemas
        return [self._recipe_to_schema(recipe) for recipe in recipes]

    def _recipe_to_schema(self, recipe: Recipe) -> RecipeSchema:
        """Convert SQLAlchemy Recipe model to Pydantic schema"""
        return RecipeSchema(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            cuisine=recipe.cuisine,
            meal_type=recipe.meal_type,
            prep_time_minutes=recipe.prep_time_minutes,
            servings=recipe.servings,
            ingredients=[
                RecipeIngredientSchema(
                    ingredient_name=ri.ingredient.name,
                    quantity=ri.quantity,
                    unit=ri.unit,
                    notes=ri.notes
                )
                for ri in recipe.recipe_ingredients
            ],
            dietary_restrictions=[dr.name for dr in recipe.dietary_restrictions]
        )

    def get_recipe_by_id(self, recipe_id: int) -> RecipeSchema:
        """Get a specific recipe by ID"""
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe:
            return self._recipe_to_schema(recipe)
        return None

    def get_all_recipes(self) -> List[RecipeSchema]:
        """Get all recipes in the database"""
        recipes = self.db.query(Recipe).all()
        return [self._recipe_to_schema(recipe) for recipe in recipes]
