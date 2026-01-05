from app.integrations.gemini_client import GeminiClient
from app.services.chat_service import ChatService
from app.domain.models import RecipeDetail, ChatMessage

recipe = RecipeDetail(
    id=1,
    title="Test Recipe",
    image=None,
    ingredients=["2 eggs", "1 tomato", "salt"],
    instructions="Beat eggs. Chop tomato. Mix together. Cook in a pan for 3-4 minutes.",
    ready_time=10,
    servings=1,
)

client = GeminiClient()
svc = ChatService(client)

history = [ChatMessage(role="user", text="Kann ich statt Tomate Paprika nehmen?")]
answer = svc.send_question(recipe, "Wie lange soll ich es braten?", history)

print("Answer:\n", answer)
