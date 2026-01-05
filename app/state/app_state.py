# app/state/app_state.py

from dataclasses import dataclass, field
from typing import List, Optional

from app.domain.models import (
    IngredientItem,
    UserPreferences,
    RecipeSummary,
    RecipeDetail,
    ChatMessage,
)


@dataclass
class AppState:
    # Final editierbare Zutatenliste
    ingredients: List[IngredientItem] = field(default_factory=list)

    # User Preferences
    preferences: UserPreferences = field(default_factory=UserPreferences)

    # Suchergebnisse
    recipes: List[RecipeSummary] = field(default_factory=list)

    # Ausgewähltes Rezept (Detailansicht)
    selected_recipe: Optional[RecipeDetail] = None

    # Chatverlauf im Detail-Screen
    chat_messages: List[ChatMessage] = field(default_factory=list)

    # Globaler Status (MVP)
    loading: bool = False
    last_error: Optional[str] = None
