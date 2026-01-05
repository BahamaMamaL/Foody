# app/integrations/spoonacular_client.py

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

from app.domain.models import RecipeSummary, RecipeDetail


class SpoonacularClient:
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("SPOONACULAR_API_KEY")
        if not self.api_key:
            raise ValueError("SPOONACULAR_API_KEY is missing (set env var or pass api_key=...)")

        self.base_url = "https://api.spoonacular.com"

    def complex_search(self, params: Dict[str, Any]) -> List[RecipeSummary]:
        url = f"{self.base_url}/recipes/complexSearch"

        # Immer apiKey rein
        full_params = dict(params)
        full_params["apiKey"] = self.api_key

        r = requests.get(url, params=full_params, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"Spoonacular complexSearch failed: {r.status_code} {r.text}")

        data = r.json()
        results = data.get("results", [])
        summaries: List[RecipeSummary] = []
        for item in results:
            summaries.append(
                RecipeSummary(
                    id=int(item["id"]),
                    title=str(item.get("title", "")),
                    image=item.get("image"),
                )
            )
        return summaries

    def get_recipe_information(self, recipe_id: int) -> RecipeDetail:
        url = f"{self.base_url}/recipes/{recipe_id}/information"
        params = {
            "apiKey": self.api_key,
            "includeNutrition": "false",
        }

        r = requests.get(url, params=params, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"Spoonacular recipe information failed: {r.status_code} {r.text}")

        data = r.json()

        # Ingredients (MVP: original strings)
        ingredients = []
        for ing in data.get("extendedIngredients", []) or []:
            original = ing.get("original")
            if original:
                ingredients.append(str(original))

        # Instructions
        instructions = (data.get("instructions") or "").strip()
        if not instructions:
            # fallback: analyzedInstructions -> steps
            analyzed = data.get("analyzedInstructions") or []
            steps_txt = []
            if analyzed and isinstance(analyzed, list):
                steps = (analyzed[0].get("steps") or []) if analyzed[0] else []
                for s in steps:
                    step = s.get("step")
                    if step:
                        steps_txt.append(str(step))
            instructions = "\n".join(steps_txt).strip()

        if not instructions:
            instructions = "No instructions available."

        return RecipeDetail(
            id=int(data["id"]),
            title=str(data.get("title", "")),
            image=data.get("image"),
            ingredients=ingredients,
            instructions=instructions,
            ready_time=data.get("readyInMinutes"),
            servings=data.get("servings"),
        )
