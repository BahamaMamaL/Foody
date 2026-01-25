# app/integrations/gemini_client.py

from __future__ import annotations

import os
from typing import List, Optional

from google import genai
from google.genai import types

from app.domain.models import ChatMessage, RecipeDetail


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash") -> None:
        # google-genai liest GEMINI_API_KEY auch automatisch, aber wir checken explizit:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing (set env var or pass api_key=...)")

        # Client init
        self.client = genai.Client(api_key=self.api_key)
        self.model = model

    def ask_about_recipe(
        self,
        recipe: RecipeDetail,
        question: str,
        history: List[ChatMessage],
    ) -> str:
        # Kontext kompakt halten (Uni-MVP)
        ingredients_block = "\n".join(f"- {x}" for x in recipe.ingredients[:40])
        instructions_block = recipe.instructions[:3000]  # nicht zu lang

        system_prompt = (
            "You are a cooking assistant embedded in a recipe application.\n\n"
            "Your task is to answer user questions about the currently selected recipe "
            "in a clear, concise, and practical way.\n\n"
            "Context available to you:\n"
            "- Recipe title\n"
            "- Ingredient list\n"
            "- Preparation instructions\n\n"
            "Rules:\n"
            "- Always respond in the same language as the user's latest message.\n"
            "- Only use the provided recipe information and general cooking knowledge.\n"
            "- Do NOT invent ingredients, steps, or cooking times that are not implied by the recipe.\n"
            "- If the requested information is not available, explicitly state this and offer a reasonable cooking-related suggestion.\n"
            "- Do not provide medical, nutritional, or dietary advice beyond general cooking tips.\n"
            "- Keep answers short and actionable unless the user explicitly asks for more detail.\n\n"
            "Tone:\n"
            "- Helpful, neutral, and professional.\n"
            "- No emojis.\n"
            "- No unnecessary introductions or disclaimers.\n\n"
            "If the question is unclear, ask a short clarification question before answering."
        )

        # History als kurzer Dialog (optional)
        history_text = ""
        for m in history[-6:]:
            prefix = "User" if m.role == "user" else "Assistant"
            history_text += f"{prefix}: {m.text}\n"

        user_prompt = (
            f"Rezept: {recipe.title}\n\n"
            f"Zutaten:\n{ingredients_block}\n\n"
            f"Anleitung:\n{instructions_block}\n\n"
            f"{history_text}"
            f"Frage: {question}\n"
        )

        resp = self.client.models.generate_content(
            model=self.model,
            contents=[user_prompt],
            config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            ),
        )

        return (resp.text or "").strip()
