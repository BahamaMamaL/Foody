from app.services.ingredient_service import IngredientService
from app.state.app_state import AppState
from app.domain.models import RecognizedIngredient

svc = IngredientService()
state = AppState()

# Manual add (dedupe + normalize)
svc.add_manual(state, " Tomato ")
svc.add_manual(state, "tomato")  # should be ignored

print("After manual adds:", state.ingredients)

# Merge detection (dedupe against existing)
detected = [
    RecognizedIngredient(name_raw="Onion", confidence=0.9),
    RecognizedIngredient(name_raw="tomato", confidence=0.8),  # already exists
]
svc.merge_detection(state, detected)
print("After merge:", state.ingredients)

# Remove
svc.remove(state, "tomato")
print("After remove tomato:", state.ingredients)
