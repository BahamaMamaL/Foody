# app/services/recipe_service.py

from __future__ import annotations

from typing import Any, Dict, List

from app.domain.constants import DIETS, INTOLERANCES, CUISINES, SORT_MODES
from app.domain.models import IngredientItem, UserPreferences, RecipeSummary, RecipeDetail
from app.integrations.spoonacular_client import SpoonacularClient


class RecipeService:
    def __init__(self, client: SpoonacularClient) -> None:
        self.client = client

    def build_complex_search_params(
        self,
        ingredients: List[IngredientItem],
        prefs: UserPreferences,
    ) -> Dict[str, Any]:
        # Zutaten sammeln
        names = sorted({i.name_norm for i in ingredients if i.name_norm.strip()})
        if not names:
            raise ValueError("No ingredients provided")

        # number clamp
        number = int(prefs.number)
        if number < 1:
            number = 1
        if number > 20:
            number = 20

        # sort validation
        sort_mode = prefs.sort_mode or "popularity"
        if sort_mode not in SORT_MODES:
            raise ValueError(f"Invalid sort_mode: {sort_mode}")

        params: Dict[str, Any] = {
            "includeIngredients": ",".join(names),
            "number": number,
            "sort": sort_mode,
            "ignorePantry": "true",
            "instructionsRequired": "true",
            "fillIngredients": "true",
        }

        # diet
        if prefs.diet is not None:
            if prefs.diet not in DIETS:
                raise ValueError(f"Invalid diet: {prefs.diet}")
            params["diet"] = prefs.diet

        # cuisine
        if prefs.cuisine is not None:
            if prefs.cuisine not in CUISINES:
                raise ValueError(f"Invalid cuisine: {prefs.cuisine}")
            params["cuisine"] = prefs.cuisine

        # intolerances
        if prefs.intolerances:
            for it in prefs.intolerances:
                if it not in INTOLERANCES:
                    raise ValueError(f"Invalid intolerance: {it}")
            params["intolerances"] = ",".join(prefs.intolerances)

        # max ready time
        if prefs.max_ready_time is not None:
            mrt = int(prefs.max_ready_time)
            if mrt < 10:
                mrt = 10
            if mrt > 120:
                mrt = 120
            params["maxReadyTime"] = mrt

        return params

    def search_recipes(self, ingredients: List[IngredientItem], prefs: UserPreferences) -> List[RecipeSummary]:
        params = self.build_complex_search_params(ingredients, prefs)
        return self.client.complex_search(params)

    def load_recipe_detail(self, recipe_id: int) -> RecipeDetail:
        return self.client.get_recipe_information(recipe_id)
