import json
import re
from typing import Dict, Any
import ollama
import os
from dotenv import load_dotenv
from ..schemas.query import ParsedQuery

load_dotenv()


class NLPParser:
    """Parses natural language queries using Ollama LLM"""

    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama2")

    def parse_query(self, query: str) -> ParsedQuery:
        """
        Parse a natural language query into structured data.

        Args:
            query: Natural language query from user

        Returns:
            ParsedQuery object with extracted information
        """
        prompt = self._create_prompt(query)

        try:
            # Call Ollama API
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract the response content
            content = response["message"]["content"]

            # Parse the JSON response
            parsed_data = self._extract_json(content)

            return ParsedQuery(**parsed_data)

        except Exception as e:
            # Fallback to basic parsing if LLM fails
            print(f"LLM parsing failed: {e}. Falling back to basic parsing.")
            return self._fallback_parse(query)

    def _create_prompt(self, query: str) -> str:
        """Create a structured prompt for the LLM"""
        return f"""You are a meal planning assistant. Parse the following natural language query and extract structured information.

User Query: "{query}"

Extract the following information and respond ONLY with a valid JSON object (no additional text):
{{
  "dietary_restrictions": ["list of dietary restrictions like vegan, gluten-free, dairy-free, vegetarian, etc."],
  "meal_types": ["list of meal types like breakfast, lunch, dinner, snack"],
  "meal_count": number of meals requested (integer or null),
  "owned_ingredients": ["list of ingredients the user already has"],
  "required_ingredients": ["list of ingredients that MUST be in the recipe, like 'ground beef', 'chicken breast', 'salmon'"],
  "cuisine_preferences": ["list of cuisine preferences like Italian, Mexican, Asian, etc."],
  "protein_requirement": minimum protein in grams per serving (integer or null),
  "other_requirements": "any other requirements or preferences as a string"
}}

Important:
- Only include fields if they are mentioned in the query
- Use empty arrays [] for lists if nothing is mentioned
- Use null for meal_count and protein_requirement if not specified
- Normalize ingredient names to lowercase
- Normalize dietary restrictions to standard terms
- "owned_ingredients" = ingredients the user ALREADY HAS
- "required_ingredients" = ingredients that MUST BE IN the recipe
- Look for protein requirements like "30g protein", "high protein", "at least 25g protein per serving"

JSON Response:"""

    def _extract_json(self, content: str) -> Dict[str, Any]:
        """Extract JSON from LLM response, handling various formats"""
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)

        # If no JSON found, try parsing the whole response
        return json.loads(content)

    def _fallback_parse(self, query: str) -> ParsedQuery:
        """Simple rule-based fallback parser if LLM fails"""
        query_lower = query.lower()

        # Extract dietary restrictions
        dietary_keywords = {
            "vegan": "vegan",
            "vegetarian": "vegetarian",
            "gluten-free": "gluten-free",
            "gluten free": "gluten-free",
            "dairy-free": "dairy-free",
            "dairy free": "dairy-free",
            "keto": "keto",
            "paleo": "paleo",
        }
        dietary_restrictions = [v for k, v in dietary_keywords.items() if k in query_lower]

        # Extract meal types
        meal_keywords = ["breakfast", "lunch", "dinner", "snack"]
        meal_types = [meal for meal in meal_keywords if meal in query_lower]

        # Extract meal count
        meal_count = None
        count_match = re.search(r'(\d+)\s*(meal|dinner|lunch|breakfast)', query_lower)
        if count_match:
            meal_count = int(count_match.group(1))

        # Extract owned ingredients (look for patterns like "I have X, Y, and Z")
        owned_ingredients = []
        have_pattern = re.search(r'(?:have|own|already have|got)\s+([^.!?]+)', query_lower)
        if have_pattern:
            ingredients_text = have_pattern.group(1)
            # Split by common delimiters
            owned_ingredients = [
                ing.strip()
                for ing in re.split(r',|\sand\s', ingredients_text)
                if ing.strip()
            ]

        return ParsedQuery(
            dietary_restrictions=dietary_restrictions,
            meal_types=meal_types,
            meal_count=meal_count,
            owned_ingredients=owned_ingredients,
            required_ingredients=[],
            cuisine_preferences=[],
            protein_requirement=None,
            other_requirements=None
        )
