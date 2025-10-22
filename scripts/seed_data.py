"""
Example script to seed the database with sample recipes.
Run with: python scripts/seed_data.py
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.base import SessionLocal, init_db
from app.models import Recipe, Ingredient, RecipeIngredient, DietaryRestriction


def seed_database():
    """Seed the database with sample data"""

    # Initialize database
    init_db()
    db = SessionLocal()

    try:
        # Create dietary restrictions
        dietary_restrictions = {
            "vegetarian": DietaryRestriction(name="vegetarian", description="No meat or fish"),
            "vegan": DietaryRestriction(name="vegan", description="No animal products"),
            "gluten-free": DietaryRestriction(name="gluten-free", description="No gluten"),
            "dairy-free": DietaryRestriction(name="dairy-free", description="No dairy products"),
        }

        for dr in dietary_restrictions.values():
            existing = db.query(DietaryRestriction).filter_by(name=dr.name).first()
            if not existing:
                db.add(dr)
        db.commit()

        # Refresh to get IDs
        for key in dietary_restrictions:
            dietary_restrictions[key] = db.query(DietaryRestriction).filter_by(name=key).first()

        # Create ingredients
        ingredients_data = [
            {"name": "black beans", "category": "pantry", "unit": "cup"},
            {"name": "rice", "category": "pantry", "unit": "cup"},
            {"name": "onion", "category": "produce", "unit": "count"},
            {"name": "garlic", "category": "produce", "unit": "clove"},
            {"name": "bell pepper", "category": "produce", "unit": "count"},
            {"name": "tomato", "category": "produce", "unit": "count"},
            {"name": "tortilla", "category": "bakery", "unit": "count"},
            {"name": "avocado", "category": "produce", "unit": "count"},
            {"name": "lime", "category": "produce", "unit": "count"},
            {"name": "cilantro", "category": "produce", "unit": "bunch"},
            {"name": "cumin", "category": "spices", "unit": "tsp"},
            {"name": "chili powder", "category": "spices", "unit": "tsp"},
            {"name": "olive oil", "category": "pantry", "unit": "tbsp"},
            {"name": "salt", "category": "pantry", "unit": "tsp"},
            {"name": "black pepper", "category": "pantry", "unit": "tsp"},
        ]

        ingredients = {}
        for ing_data in ingredients_data:
            existing = db.query(Ingredient).filter_by(name=ing_data["name"]).first()
            if not existing:
                ing = Ingredient(**ing_data)
                db.add(ing)
                db.commit()
                ingredients[ing_data["name"]] = ing
            else:
                ingredients[ing_data["name"]] = existing

        # Create sample recipes
        recipes_data = [
            {
                "name": "Black Bean Tacos",
                "description": "Simple and delicious vegetarian tacos",
                "cuisine": "Mexican",
                "meal_type": "dinner",
                "prep_time_minutes": 20,
                "servings": 4,
                "dietary_restrictions": ["vegetarian"],
                "ingredients": [
                    {"name": "black beans", "quantity": 2, "unit": "cup", "notes": "cooked"},
                    {"name": "onion", "quantity": 1, "unit": "count", "notes": "diced"},
                    {"name": "garlic", "quantity": 2, "unit": "clove", "notes": "minced"},
                    {"name": "cumin", "quantity": 1, "unit": "tsp"},
                    {"name": "chili powder", "quantity": 1, "unit": "tsp"},
                    {"name": "tortilla", "quantity": 8, "unit": "count"},
                    {"name": "avocado", "quantity": 1, "unit": "count", "notes": "sliced"},
                    {"name": "lime", "quantity": 1, "unit": "count"},
                ]
            },
            {
                "name": "Vegetarian Burrito Bowl",
                "description": "Healthy and filling burrito bowl",
                "cuisine": "Mexican",
                "meal_type": "dinner",
                "prep_time_minutes": 25,
                "servings": 4,
                "dietary_restrictions": ["vegetarian"],
                "ingredients": [
                    {"name": "rice", "quantity": 2, "unit": "cup", "notes": "cooked"},
                    {"name": "black beans", "quantity": 2, "unit": "cup", "notes": "cooked"},
                    {"name": "bell pepper", "quantity": 2, "unit": "count", "notes": "diced"},
                    {"name": "onion", "quantity": 1, "unit": "count", "notes": "diced"},
                    {"name": "tomato", "quantity": 2, "unit": "count", "notes": "diced"},
                    {"name": "avocado", "quantity": 2, "unit": "count", "notes": "sliced"},
                    {"name": "lime", "quantity": 2, "unit": "count"},
                    {"name": "cilantro", "quantity": 0.25, "unit": "bunch"},
                ]
            },
            {
                "name": "Simple Rice and Beans",
                "description": "Classic rice and beans dish",
                "cuisine": "Latin",
                "meal_type": "dinner",
                "prep_time_minutes": 15,
                "servings": 4,
                "dietary_restrictions": ["vegetarian", "vegan", "gluten-free", "dairy-free"],
                "ingredients": [
                    {"name": "rice", "quantity": 2, "unit": "cup", "notes": "cooked"},
                    {"name": "black beans", "quantity": 2, "unit": "cup", "notes": "cooked"},
                    {"name": "onion", "quantity": 1, "unit": "count", "notes": "diced"},
                    {"name": "garlic", "quantity": 3, "unit": "clove", "notes": "minced"},
                    {"name": "cumin", "quantity": 1, "unit": "tsp"},
                    {"name": "olive oil", "quantity": 2, "unit": "tbsp"},
                    {"name": "salt", "quantity": 1, "unit": "tsp"},
                    {"name": "black pepper", "quantity": 0.5, "unit": "tsp"},
                ]
            }
        ]

        for recipe_data in recipes_data:
            # Check if recipe already exists
            existing = db.query(Recipe).filter_by(name=recipe_data["name"]).first()
            if existing:
                print(f"Recipe '{recipe_data['name']}' already exists, skipping...")
                continue

            # Create recipe
            recipe = Recipe(
                name=recipe_data["name"],
                description=recipe_data["description"],
                cuisine=recipe_data["cuisine"],
                meal_type=recipe_data["meal_type"],
                prep_time_minutes=recipe_data["prep_time_minutes"],
                servings=recipe_data["servings"]
            )

            # Add dietary restrictions
            for dr_name in recipe_data["dietary_restrictions"]:
                recipe.dietary_restrictions.append(dietary_restrictions[dr_name])

            db.add(recipe)
            db.commit()

            # Add recipe ingredients
            for ing_data in recipe_data["ingredients"]:
                ingredient = ingredients[ing_data["name"]]
                recipe_ing = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                    quantity=ing_data["quantity"],
                    unit=ing_data["unit"],
                    notes=ing_data.get("notes")
                )
                db.add(recipe_ing)

            db.commit()
            print(f"Created recipe: {recipe_data['name']}")

        print("\nDatabase seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
