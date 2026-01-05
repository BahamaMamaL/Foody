from app.domain.models import UserPreferences, IngredientItem

prefs = UserPreferences()
print("prefs OK:", prefs)

item = IngredientItem(name_raw="Tomato", name_norm="tomato", source="yolo")
print("item OK:", item)
