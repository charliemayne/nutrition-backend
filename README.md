# Nutrition Query Backend

A backend service that processes natural language meal planning queries and generates optimized grocery lists.

## Features

- **Natural Language Processing**: Parse queries like "I want 3 vegan dinners this week and I already have rice and beans"
- **Recipe Matching**: Find recipes based on dietary restrictions, meal types, and preferences
- **Grocery List Generation**: Automatically aggregate ingredients across recipes and deduplicate
- **Owned Ingredients**: Filter out items you already have
- **Future-Ready**: Built with hooks for price optimization, store proximity, and quality scoring

## Architecture

```
app/
├── models/          # SQLAlchemy database models
├── schemas/         # Pydantic schemas for API
├── services/        # Business logic
│   ├── nlp_parser.py              # Natural language query parsing
│   ├── recipe_matcher.py          # Recipe suggestion engine
│   └── grocery_list_generator.py  # Grocery list creation
└── api/             # FastAPI routes
```

## Setup

### Prerequisites

1. **Python 3.9+**
2. **Ollama** (for free local LLM)
   - Install: https://ollama.ai
   - Pull a model: `ollama pull llama2`

### Installation

1. Clone the repository and navigate to the project directory

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env if needed (default values work for local development)
```

5. Make sure Ollama is running:
```bash
ollama serve
```

## Running the Server

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

## API Usage

### Process a Natural Language Query

**POST** `/api/v1/query`

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want to make 3 vegetarian dinners this week. I already have rice, onions, and garlic."
  }'
```

**Response:**
```json
{
  "parsed_query": {
    "dietary_restrictions": ["vegetarian"],
    "meal_types": ["dinner"],
    "meal_count": 3,
    "owned_ingredients": ["rice", "onions", "garlic"],
    "cuisine_preferences": [],
    "other_requirements": null
  },
  "suggested_recipes": [...],
  "grocery_list": [
    {
      "ingredient_name": "black beans",
      "total_quantity": 2.0,
      "unit": "cup",
      "category": "pantry",
      "recipes_used_in": ["Black Bean Tacos", "Bean Burrito Bowl"],
      "already_owned": false
    },
    ...
  ],
  "total_estimated_cost": null
}
```

### Get All Recipes

**GET** `/api/v1/recipes`

### Get Specific Recipe

**GET** `/api/v1/recipes/{recipe_id}`

## Adding Recipes

To add recipes to the database, you can:

1. Create a script to populate the database (see `scripts/seed_data.py` example)
2. Use the database directly via SQLAlchemy
3. Build admin endpoints (future feature)

Example of adding a recipe programmatically:

```python
from app.models.base import SessionLocal, init_db
from app.models import Recipe, Ingredient, RecipeIngredient, DietaryRestriction

# Initialize database
init_db()
db = SessionLocal()

# Create an ingredient
tomato = Ingredient(name="tomato", category="produce", unit="count")
db.add(tomato)
db.commit()

# Create a dietary restriction
vegetarian = DietaryRestriction(name="vegetarian")
db.add(vegetarian)
db.commit()

# Create a recipe
recipe = Recipe(
    name="Tomato Salad",
    description="Simple tomato salad",
    meal_type="lunch",
    servings=2
)
recipe.dietary_restrictions.append(vegetarian)
db.add(recipe)
db.commit()

# Link ingredient to recipe
recipe_ing = RecipeIngredient(
    recipe_id=recipe.id,
    ingredient_id=tomato.id,
    quantity=2,
    unit="count",
    notes="diced"
)
db.add(recipe_ing)
db.commit()
```

## Using Different LLM Providers

### Switch to OpenAI (Paid)

1. Install: `pip install openai`
2. Modify `app/services/nlp_parser.py` to use OpenAI API
3. Add `OPENAI_API_KEY` to `.env`

### Switch to Anthropic Claude (Paid)

1. Install: `pip install anthropic`
2. Modify `app/services/nlp_parser.py` to use Anthropic API
3. Add `ANTHROPIC_API_KEY` to `.env`

## Future Enhancements

- [ ] Store proximity optimization (requires store location data)
- [ ] Price comparison across stores
- [ ] Ingredient availability checking
- [ ] Quality/rating scores for ingredients
- [ ] Optimal store routing
- [ ] User accounts and saved preferences
- [ ] Recipe rating and review system
- [ ] Meal plan calendar
- [ ] Nutritional information tracking

## Development

### Project Structure

- `app/models/` - Database models (SQLAlchemy ORM)
- `app/schemas/` - API request/response schemas (Pydantic)
- `app/services/` - Business logic services
- `app/api/` - API route handlers
- `requirements.txt` - Python dependencies

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest
```

## License

MIT
