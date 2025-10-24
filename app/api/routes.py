from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..models.base import get_db
from ..schemas.query import QueryRequest, QueryResponse
from ..schemas.recipe import RecipeSchema
from ..schemas.ingredient import IngredientSchema
from ..schemas.url_fetch import URLFetchRequest, URLFetchResponse, SupportedSitesResponse
from ..services import NLPParser, RecipeMatcher, GroceryListGenerator, RecipeFetcher, RecipeFetcherError, RecipeSearcher

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Process a natural language query and return suggested recipes and grocery list.

    This endpoint:
    1. Parses the natural language query
    2. Searches local database for matching recipes
    3. If insufficient results, searches the web for recipe URLs (using Ollama)
    4. Fetches recipes from discovered URLs (respecting robots.txt and rate limits)
    5. Generates a consolidated grocery list
    6. Removes items the user already owns

    Example queries:
    - "I want bodybuilding meal prep dinners that use ground beef and have at least 30g protein per serving"
    - "Find me 5 vegan Mexican recipes with black beans"
    - "High protein chicken dinners for this week"
    """
    try:
        # Step 1: Parse the natural language query
        nlp_parser = NLPParser()
        parsed_query = nlp_parser.parse_query(request.query)

        # Step 2: Find matching recipes in local database
        recipe_matcher = RecipeMatcher(db)
        suggested_recipes = recipe_matcher.find_matching_recipes(parsed_query)

        recipes_from_web = 0
        search_performed = False

        # Step 3: If we don't have enough recipes, search the web
        desired_count = parsed_query.meal_count or 5
        if len(suggested_recipes) < desired_count:
            print(f"Found {len(suggested_recipes)} recipes in database. Searching web for more...")
            search_performed = True

            # Search the web for recipe URLs
            searcher = RecipeSearcher()
            recipe_urls = searcher.search_recipes(
                parsed_query,
                max_results=desired_count - len(suggested_recipes)
            )

            print(f"Found {len(recipe_urls)} potential recipe URLs")

            # Step 4: Fetch recipes from URLs
            fetcher = RecipeFetcher(db=db)

            for url in recipe_urls:
                try:
                    print(f"Attempting to fetch: {url}")

                    # Check if URL is supported and allowed
                    if not fetcher.is_url_supported(url):
                        print(f"  Skipping: unsupported site")
                        continue

                    if not fetcher.check_robots_txt(url):
                        print(f"  Skipping: robots.txt disallows")
                        continue

                    # Fetch recipe and save to DB for future use
                    recipe = fetcher.fetch_recipe_from_url(url, save_to_db=True)
                    suggested_recipes.append(recipe)
                    recipes_from_web += 1

                    print(f"  ✓ Fetched and saved: {recipe.name}")

                    # Stop if we have enough
                    if len(suggested_recipes) >= desired_count:
                        break

                except RecipeFetcherError as e:
                    print(f"  Failed to fetch {url}: {e}")
                    continue
                except Exception as e:
                    print(f"  Unexpected error fetching {url}: {e}")
                    continue

            print(f"Total recipes after web search: {len(suggested_recipes)} ({recipes_from_web} from web)")

        # Step 5: Generate grocery list
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
            total_estimated_cost=total_cost if total_cost > 0 else None,
            recipes_from_web=recipes_from_web,
            search_performed=search_performed
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


@router.post("/recipes/fetch-from-url", response_model=URLFetchResponse)
async def fetch_recipe_from_url(request: URLFetchRequest, db: Session = Depends(get_db)):
    """
    Fetch a recipe from a URL and optionally save it to the database.

    LEGAL NOTICE:
    - This endpoint respects robots.txt and website policies
    - Only works with supported recipe sites (100+ sites including AllRecipes, Food Network, etc.)
    - Implements rate limiting to avoid overwhelming servers
    - Recipe content belongs to original publishers - always attribute sources
    - For personal and educational use only

    Args:
        request: URLFetchRequest with URL and save_to_db flag
        db: Database session

    Returns:
        URLFetchResponse with fetched recipe data
    """
    try:
        fetcher = RecipeFetcher(db=db)

        # Fetch recipe
        recipe = fetcher.fetch_recipe_from_url(
            url=request.url,
            save_to_db=request.save_to_db
        )

        message = "Recipe fetched successfully"
        if request.save_to_db:
            message += " and saved to database"

        return URLFetchResponse(
            success=True,
            message=message,
            recipe=recipe.model_dump(),
            source_url=request.url
        )

    except RecipeFetcherError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recipe: {str(e)}")


@router.get("/recipes/supported-sites", response_model=SupportedSitesResponse)
async def get_supported_sites():
    """
    Get a list of supported recipe websites.

    Returns:
        List of website domains that can be scraped for recipes
    """
    try:
        fetcher = RecipeFetcher()
        sites = fetcher.get_supported_sites_list()

        return SupportedSitesResponse(
            supported_sites=sites,
            total_count=len(sites),
            message=f"This API supports fetching recipes from {len(sites)} websites"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting supported sites: {str(e)}")
