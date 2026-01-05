from app.state.app_state import AppState

state = AppState()
print("ingredients:", state.ingredients)
print("preferences:", state.preferences)
print("recipes:", state.recipes)
print("selected_recipe:", state.selected_recipe)
print("chat_messages:", state.chat_messages)
