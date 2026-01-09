# app/integrations/spoonacular_client.py

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

from app.domain.models import RecipeSummary, RecipeDetail


def _fmt_amount(value: float) -> str:
    """
    Format numbers in a human-friendly way:
    1.0   -> 1
    2.50  -> 2.5
    33.3333 -> 33.3
    """
    try:
        if float(value).is_integer():
            return str(int(value))
        return f"{float(value):.2f}".rstrip("0").rstrip(".")
    except Exception:
        return str(value)


class SpoonacularClient:
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("SPOONACULAR_API_KEY")
        if not self.api_key:
            raise ValueError("SPOONACULAR_API_KEY is missing (set env var or pass api_key=...)")

        self.base_url = "https://api.spoonacular.com"

    # ---------------------------------------------------------
    # SEARCH (complexSearch)
    # ---------------------------------------------------------
    def complex_search(self, params: Dict[str, Any]) -> List[RecipeSummary]:
        url = f"{self.base_url}/recipes/complexSearch"

        full_params = dict(params)
        full_params["apiKey"] = self.api_key

        r = requests.get(url, params=full_params, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"Spoonacular complexSearch failed: {r.status_code} {r.text}")

        data = r.json()
        results = data.get("results", [])
        summaries: List[RecipeSummary] = []

        def _pick_name(x: dict) -> str:
            return str(
                x.get("name")
                or x.get("originalName")
                or x.get("original")
                or ""
            ).strip()

        for item in results:
            used_list: Optional[List[str]] = None
            missed_list: Optional[List[str]] = None

            if isinstance(item.get("usedIngredients"), list):
                used_list = [_pick_name(x) for x in item["usedIngredients"] if isinstance(x, dict)]
                used_list = [x for x in used_list if x]

            if isinstance(item.get("missedIngredients"), list):
                missed_list = [_pick_name(x) for x in item["missedIngredients"] if isinstance(x, dict)]
                missed_list = [x for x in missed_list if x]

            summaries.append(
                RecipeSummary(
                    id=int(item["id"]),
                    title=str(item.get("title", "")),
                    image=item.get("image"),
                    used_ingredient_count=item.get("usedIngredientCount"),
                    missed_ingredient_count=item.get("missedIngredientCount"),
                    used_ingredients=used_list,
                    missed_ingredients=missed_list,
                )
            )

        return summaries

    # ---------------------------------------------------------
    # DETAIL (metric-only ingredients)
    # ---------------------------------------------------------
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

        # --- Ingredients (metric only, human friendly) ---
        ingredients: List[str] = []
        for ing in data.get("extendedIngredients", []) or []:
            measures = (ing.get("measures") or {}).get("metric") or {}
            amount = measures.get("amount")
            unit = measures.get("unitShort") or measures.get("unitLong")
            name = ing.get("name")

            if amount is not None and unit and name:
                ingredients.append(f"{_fmt_amount(float(amount))} {unit} {name}")
            elif name:
                # fallback if metric info is missing
                ingredients.append(str(name))

        # --- Alternative: ORIGINAL ingredient strings (US / mixed units) ---
        # ingredients: List[str] = []
        # for ing in data.get("extendedIngredients", []) or []:
        #     original = ing.get("original")
        #     if original:
        #         ingredients.append(str(original))

        # --- Instructions ---
        instructions = (data.get("instructions") or "").strip()
        if not instructions:
            analyzed = data.get("analyzedInstructions") or []
            steps_txt: List[str] = []
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
