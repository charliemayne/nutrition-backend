"""
Simple script to test the NLP query parser without running the full API.
Run with: python scripts/test_query.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.nlp_parser import NLPParser


def test_queries():
    """Test various natural language queries"""

    parser = NLPParser()

    test_cases = [
        "I want to make 3 vegetarian dinners this week. I already have rice, onions, and garlic.",
        "I need 5 gluten-free meals for the week",
        "Plan vegan breakfast and lunch for 4 days. I have oats and bananas.",
        "I want Italian dinner recipes. I'm dairy-free and have tomatoes.",
        "Give me 2 quick dinners under 30 minutes",
    ]

    print("Testing NLP Query Parser\n" + "="*50 + "\n")

    for query in test_cases:
        print(f"Query: {query}")
        print("-" * 50)

        try:
            result = parser.parse_query(query)
            print(f"Dietary Restrictions: {result.dietary_restrictions}")
            print(f"Meal Types: {result.meal_types}")
            print(f"Meal Count: {result.meal_count}")
            print(f"Owned Ingredients: {result.owned_ingredients}")
            print(f"Cuisine Preferences: {result.cuisine_preferences}")
            print(f"Other Requirements: {result.other_requirements}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n")


if __name__ == "__main__":
    test_queries()
