# app/services/chat_service.py

from __future__ import annotations

from typing import List

from app.domain.models import ChatMessage, RecipeDetail
from app.integrations.gemini_client import GeminiClient


class ChatService:
    def __init__(self, client: GeminiClient) -> None:
        self.client = client

    def send_question(self, recipe: RecipeDetail, question: str, history: List[ChatMessage]) -> str:
        q = question.strip()
        if not q:
            return ""
        return self.client.ask_about_recipe(recipe, q, history)
