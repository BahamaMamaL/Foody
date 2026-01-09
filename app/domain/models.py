# app/domain/models.py

from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass
from typing import Optional, List, Literal


@dataclass(frozen=True)
class RecognizedIngredient:
    name_raw: str
    confidence: Optional[float] = None
    source: Literal["yolo"] = "yolo"


@dataclass(frozen=True)
class IngredientItem:
    name_raw: str
    name_norm: str
    source: Literal["yolo", "manual"]


@dataclass
class UserPreferences:
    diet: Optional[str] = None
    intolerances: List[str] = None
    cuisine: Optional[str] = None
    number: int = 10
    max_ready_time: Optional[int] = None
    sort_mode: str = "popularity"

    def __post_init__(self) -> None:
        if self.intolerances is None:
            self.intolerances = []


@dataclass(frozen=True)
class RecipeSummary:
    id: int
    title: str
    image: Optional[str] = None

    # NEW (optional, kommt von Spoonacular wenn fillIngredients=true)
    used_ingredient_count: Optional[int] = None
    missed_ingredient_count: Optional[int] = None
    used_ingredients: Optional[List[str]] = None
    missed_ingredients: Optional[List[str]] = None


@dataclass(frozen=True)
class RecipeDetail:
    id: int
    title: str
    image: Optional[str]
    ingredients: List[str]
    instructions: str
    ready_time: Optional[int] = None
    servings: Optional[int] = None


@dataclass(frozen=True)
class ChatMessage:
    role: Literal["user", "assistant"]
    text: str
