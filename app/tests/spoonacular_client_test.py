from app.integrations.spoonacular_client import SpoonacularClient

client = SpoonacularClient()

params = {
    "includeIngredients": "tomato,cheese",
    "number": 3,
    "sort": "popularity",
    "ignorePantry": "true",
}

recipes = client.complex_search(params)
print("Found:", len(recipes))
for r in recipes:
    print(r.id, "-", r.title)

if recipes:
    detail = client.get_recipe_information(recipes[0].id)
    print("\nDETAIL:", detail.title)
    print("Ingredients sample:", detail.ingredients[:3])
    print("Instructions sample:", detail.instructions[:200])
