from app.domain.models import IngredientItem, UserPreferences
from app.integrations.spoonacular_client import SpoonacularClient
from app.services.recipe_service import RecipeService

client = SpoonacularClient()
service = RecipeService(client)

ingredients = [
    IngredientItem(name_raw="Tomato", name_norm="tomato", source="manual"),
    IngredientItem(name_raw="Cheese", name_norm="cheese", source="manual"),
]

prefs = UserPreferences(
    diet=None,
    intolerances=[],
    cuisine=None,
    number=3,
    max_ready_time=45,
    sort_mode="popularity",
)

recipes = service.search_recipes(ingredients, prefs)
print("Found:", len(recipes))
for r in recipes:
    print(r.id, r.title)

if recipes:
    detail = service.load_recipe_detail(recipes[0].id)
    print("\nDETAIL:", detail.title)
    print("Ingredients:", len(detail.ingredients))
    print("Instructions chars:", len(detail.instructions))
