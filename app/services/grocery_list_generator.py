from typing import List, Dict
from collections import defaultdict
from ..schemas.recipe import RecipeSchema
from ..schemas.ingredient import GroceryListItem


class GroceryListGenerator:
    """Generates and optimizes grocery lists from recipes"""

    def generate_grocery_list(
        self,
        recipes: List[RecipeSchema],
        owned_ingredients: List[str] = None
    ) -> List[GroceryListItem]:
        """
        Generate a consolidated grocery list from multiple recipes.

        Args:
            recipes: List of recipes to create grocery list from
            owned_ingredients: List of ingredient names the user already has

        Returns:
            List of grocery items with aggregated quantities
        """
        if owned_ingredients is None:
            owned_ingredients = []

        # Normalize owned ingredients to lowercase for comparison
        owned_set = {ing.lower().strip() for ing in owned_ingredients}

        # Aggregate ingredients across all recipes
        # Key: (ingredient_name, unit), Value: {total_quantity, recipes, category}
        aggregated: Dict[tuple, dict] = defaultdict(lambda: {
            "total_quantity": 0.0,
            "recipes": [],
            "category": None
        })

        for recipe in recipes:
            for ingredient in recipe.ingredients:
                key = (ingredient.ingredient_name.lower(), ingredient.unit)

                aggregated[key]["total_quantity"] += ingredient.quantity
                aggregated[key]["recipes"].append(recipe.name)
                # Category would come from the Ingredient model if we had it loaded

        # Convert to GroceryListItem objects
        grocery_list = []
        for (ingredient_name, unit), data in aggregated.items():
            is_owned = ingredient_name in owned_set

            grocery_list.append(
                GroceryListItem(
                    ingredient_name=ingredient_name,
                    total_quantity=round(data["total_quantity"], 2),
                    unit=unit,
                    category=data["category"],
                    recipes_used_in=list(set(data["recipes"])),  # Remove duplicates
                    already_owned=is_owned
                )
            )

        # Sort grocery list by category (if available) and then by name
        grocery_list.sort(key=lambda x: (x.category or "zzz", x.ingredient_name))

        return grocery_list

    def optimize_grocery_list(
        self,
        grocery_list: List[GroceryListItem],
        user_location: str = None
    ) -> List[GroceryListItem]:
        """
        Optimize grocery list based on availability, proximity, quality, and price.
        This is a placeholder for future implementation.

        Args:
            grocery_list: Unoptimized grocery list
            user_location: User's location for proximity optimization

        Returns:
            Optimized grocery list
        """
        # TODO: Implement optimization logic
        # This would involve:
        # 1. Checking ingredient availability at nearby stores
        # 2. Calculating proximity scores
        # 3. Comparing quality ratings
        # 4. Finding best prices
        # 5. Suggesting store routing

        # For now, just return the original list
        return grocery_list

    def filter_owned_ingredients(
        self,
        grocery_list: List[GroceryListItem]
    ) -> List[GroceryListItem]:
        """
        Filter out ingredients the user already owns.

        Args:
            grocery_list: Full grocery list

        Returns:
            Grocery list with owned ingredients removed
        """
        return [item for item in grocery_list if not item.already_owned]

    def calculate_estimated_cost(
        self,
        grocery_list: List[GroceryListItem]
    ) -> float:
        """
        Calculate estimated total cost of grocery list.
        This is a placeholder for future implementation.

        Args:
            grocery_list: Grocery list to estimate cost for

        Returns:
            Estimated total cost in dollars
        """
        # TODO: Implement cost calculation
        # This would involve looking up prices from stores or price databases
        return 0.0
