from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

from app.state.app_state import AppState
from app.services.recipe_service import RecipeService


class ResultsScreen(QWidget):
    def __init__(
        self,
        state: AppState,
        recipe_service: RecipeService,
        on_back,
        on_open_detail,
    ) -> None:
        super().__init__()
        self.state = state
        self.recipe_service = recipe_service
        self.on_back = on_back
        self.on_open_detail = on_open_detail

        root = QVBoxLayout()

        title = QLabel("Recipe results")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        root.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.handle_open_selected)
        root.addWidget(self.list_widget)

        buttons = QHBoxLayout()

        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.on_back)
        buttons.addWidget(back_btn)

        open_btn = QPushButton("Open selected")
        open_btn.clicked.connect(self.handle_open_selected)
        buttons.addWidget(open_btn)

        root.addLayout(buttons)
        self.setLayout(root)

        self.refresh()

    def refresh(self) -> None:
        self.list_widget.clear()
        for r in self.state.recipes:
            # Store recipe_id in item text (simple MVP)
            self.list_widget.addItem(f"{r.id} - {r.title}")

    def _selected_recipe_id(self) -> int | None:
        row = self.list_widget.currentRow()
        if row < 0:
            return None
        if row >= len(self.state.recipes):
            return None
        return self.state.recipes[row].id

    def handle_open_selected(self) -> None:
        recipe_id = self._selected_recipe_id()
        if recipe_id is None:
            QMessageBox.information(self, "Select a recipe", "Please select a recipe first.")
            return

        try:
            # blocking load (MVP)
            detail = self.recipe_service.load_recipe_detail(recipe_id)
            self.state.selected_recipe = detail

            # Chat reset for new recipe (makes UX clean)
            self.state.chat_messages = []

            self.on_open_detail()

        except Exception as e:
            QMessageBox.critical(self, "Failed to load recipe", str(e))
