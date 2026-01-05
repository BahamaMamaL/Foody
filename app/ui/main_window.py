from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from app.state.app_state import AppState
from app.services.ingredient_service import IngredientService
from app.services.detection_service import DetectionService
from app.integrations.spoonacular_client import SpoonacularClient
from app.services.recipe_service import RecipeService
from app.integrations.gemini_client import GeminiClient
from app.services.chat_service import ChatService

from app.ui.screens.scan_screen import ScanScreen
from app.ui.screens.ingredient_review_screen import IngredientReviewScreen
from app.ui.screens.preferences_screen import PreferencesScreen
from app.ui.screens.results_screen import ResultsScreen
from app.ui.screens.detail_screen import DetailScreen

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Foody")
        self.resize(1000, 700)

        # --- App State ---
        self.state = AppState()

        # --- Services / Clients ---
        self.ingredient_service = IngredientService()

        # Modellpfad: (relativ zur Working Directory = Projekt-Root)
        self.detection_service = DetectionService(model_path="models/best(10).pt")

        self.spoon_client = SpoonacularClient()
        self.recipe_service = RecipeService(self.spoon_client)

        self.gemini_client = GeminiClient()
        self.chat_service = ChatService(self.gemini_client)

        # --- Navigation Container ---
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # --- Screens ---
        self.scan_screen = ScanScreen(
            state=self.state,
            detection_service=self.detection_service,
            ingredient_service=self.ingredient_service,
            on_next=self.go_to_review,
            camera_index=0,
        )

        self.review_screen = IngredientReviewScreen(
            state=self.state,
            ingredient_service=self.ingredient_service,
            on_back=self.go_to_scan,
            on_next=self.go_to_preferences,
        )

        self.preferences_screen = PreferencesScreen(
            state=self.state,
            recipe_service=self.recipe_service,
            on_back=self.go_to_review,
            on_next=self.go_to_results,  # kommt im nächsten Schritt
        )

        self.results_screen = ResultsScreen(
            state=self.state,
            recipe_service=self.recipe_service,
            on_back=self.go_to_preferences,
            on_open_detail=self.go_to_detail,  # kommt im nächsten Schritt
        )

        self.detail_screen = DetailScreen(
            state=self.state,
            chat_service=self.chat_service,
            on_back=self.go_to_results,
        )

        # Stack order
        self.stack.addWidget(self.scan_screen)         # index 0
        self.stack.addWidget(self.review_screen)       # index 1
        self.stack.addWidget(self.preferences_screen)  # index 2
        self.stack.addWidget(self.results_screen)      # index 3
        self.stack.addWidget(self.detail_screen)       # index 4


        self.go_to_scan()

    def go_to_scan(self) -> None:
        self.stack.setCurrentIndex(0)
        self.scan_screen.refresh()

    def go_to_review(self) -> None:
        self.stack.setCurrentIndex(1)
        self.review_screen.refresh()

    def go_to_preferences(self) -> None:
        self.stack.setCurrentIndex(2)
        self.preferences_screen.load_from_state()

    def go_to_results(self) -> None:
        self.stack.setCurrentIndex(3)
        self.results_screen.refresh()

    def go_to_detail(self) -> None:
        self.stack.setCurrentIndex(4)
        self.detail_screen.refresh()



