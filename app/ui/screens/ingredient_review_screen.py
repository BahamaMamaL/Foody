from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
)

from app.state.app_state import AppState
from app.services.ingredient_service import IngredientService


class IngredientReviewScreen(QWidget):
    def __init__(
        self,
        state: AppState,
        ingredient_service: IngredientService,
        on_back,
        on_next,
    ) -> None:
        super().__init__()
        self.state = state
        self.ingredient_service = ingredient_service
        self.on_back = on_back
        self.on_next = on_next

        root = QVBoxLayout()

        title = QLabel("Review ingredients")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        root.addWidget(title)

        self.list_widget = QListWidget()
        root.addWidget(self.list_widget)

        # Add row
        add_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Add ingredient (e.g. tomato)")
        add_row.addWidget(self.input)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.handle_add)
        add_row.addWidget(add_btn)

        root.addLayout(add_row)

        # Remove button
        rm_btn = QPushButton("Remove selected")
        rm_btn.clicked.connect(self.handle_remove_selected)
        root.addWidget(rm_btn)

        # Navigation buttons
        nav = QHBoxLayout()
        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.on_back)
        nav.addWidget(back_btn)

        next_btn = QPushButton("Weiter")
        next_btn.clicked.connect(self.handle_next)
        nav.addWidget(next_btn)

        root.addLayout(nav)

        self.setLayout(root)
        self.refresh()

    def refresh(self) -> None:
        self.list_widget.clear()
        for item in self.state.ingredients:
            self.list_widget.addItem(f"{item.name_raw} ({item.source})")

    def handle_add(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        self.ingredient_service.add_manual(self.state, text)
        self.input.clear()
        self.refresh()

    def handle_remove_selected(self) -> None:
        row = self.list_widget.currentRow()
        if row < 0:
            return
        # remove by name_norm using state index
        item = self.state.ingredients[row]
        self.ingredient_service.remove(self.state, item.name_norm)
        self.refresh()

    def handle_next(self) -> None:
        if not self.state.ingredients:
            QMessageBox.warning(self, "No ingredients", "Please add at least one ingredient.")
            return
        self.on_next()
