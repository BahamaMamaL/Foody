# app/services/ingredient_service.py

from __future__ import annotations

from typing import List

from app.domain.models import IngredientItem, RecognizedIngredient
from app.state.app_state import AppState


class IngredientService:
    @staticmethod
    def normalize(name: str) -> str:
        # MVP: nur trim + lowercase
        return name.strip().lower()

    @staticmethod
    def _exists(state: AppState, name_norm: str) -> bool:
        return any(item.name_norm == name_norm for item in state.ingredients)

    def add_manual(self, state: AppState, name_raw: str) -> None:
        norm = self.normalize(name_raw)
        if not norm:
            return
        if self._exists(state, norm):
            return

        state.ingredients.append(
            IngredientItem(
                name_raw=name_raw.strip(),
                name_norm=norm,
                source="manual",
            )
        )

    def remove(self, state: AppState, name_norm: str) -> None:
        state.ingredients = [i for i in state.ingredients if i.name_norm != name_norm]

    def merge_detection(self, state: AppState, detected: List[RecognizedIngredient]) -> None:
        for d in detected:
            norm = self.normalize(d.name_raw)
            if not norm:
                continue
            if self._exists(state, norm):
                continue

            state.ingredients.append(
                IngredientItem(
                    name_raw=d.name_raw.strip(),
                    name_norm=norm,
                    source="yolo",
                )
            )
