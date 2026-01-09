from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QSlider,
    QMessageBox,
)

from app.domain.constants import DIETS, INTOLERANCES, CUISINES, SORT_MODES
from app.state.app_state import AppState
from app.services.recipe_service import RecipeService


class PreferencesScreen(QWidget):
    def __init__(
        self,
        state: AppState,
        recipe_service: RecipeService,
        on_back,
        on_next,
    ) -> None:
        super().__init__()
        self.state = state
        self.recipe_service = recipe_service
        self.on_back = on_back
        self.on_next = on_next

        root = QVBoxLayout()

        title = QLabel("Preferences")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        root.addWidget(title)

        # --- Diet ---
        root.addWidget(QLabel("Diet"))
        self.diet_combo = QComboBox()
        for d in DIETS:
            self.diet_combo.addItem("None" if d is None else d, d)
        root.addWidget(self.diet_combo)

        # --- Cuisine ---
        root.addWidget(QLabel("Cuisine"))
        self.cuisine_combo = QComboBox()
        for c in CUISINES:
            self.cuisine_combo.addItem("None" if c is None else c, c)
        root.addWidget(self.cuisine_combo)

        # --- Intolerances (collapsible, expanded by default) ---
        root.addWidget(QLabel("Intolerances"))

        self.intol_toggle_btn = QPushButton("Hide")
        self.intol_toggle_btn.setCheckable(True)
        self.intol_toggle_btn.setChecked(True)
        self.intol_toggle_btn.clicked.connect(self._toggle_intolerances)
        root.addWidget(self.intol_toggle_btn)

        self.intol_container = QWidget()
        intol_layout = QVBoxLayout()
        intol_layout.setContentsMargins(10, 0, 0, 0)
        self.intol_container.setLayout(intol_layout)

        self.intolerance_boxes: list[QCheckBox] = []
        for it in INTOLERANCES:
            cb = QCheckBox(it)
            self.intolerance_boxes.append(cb)
            intol_layout.addWidget(cb)

        self.intol_container.setVisible(True)
        root.addWidget(self.intol_container)

        # --- Sort ---
        root.addWidget(QLabel("Sort by"))
        self.sort_combo = QComboBox()
        for s in SORT_MODES:
            self.sort_combo.addItem(s)
        root.addWidget(self.sort_combo)

        # --- Number of recipes ---
        root.addWidget(QLabel("Number of recipes"))
        self.number_spin = QSpinBox()
        self.number_spin.setRange(1, 20)
        self.number_spin.setValue(10)
        root.addWidget(self.number_spin)

        # --- maxReadyTime (optional) ---
        root.addWidget(QLabel("Max ready time"))

        time_row = QHBoxLayout()
        self.time_enabled = QCheckBox("Enable time limit")
        self.time_enabled.setChecked(False)
        self.time_enabled.stateChanged.connect(self._toggle_time_limit)
        time_row.addWidget(self.time_enabled)

        self.time_label = QLabel("30 minutes")
        time_row.addWidget(self.time_label)

        root.addLayout(time_row)

        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(10, 120)
        self.time_slider.setValue(30)
        self.time_slider.setEnabled(False)
        self.time_slider.valueChanged.connect(lambda v: self.time_label.setText(f"{v} minutes"))
        root.addWidget(self.time_slider)

        # --- Navigation buttons ---
        nav = QHBoxLayout()

        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.on_back)
        nav.addWidget(back_btn)

        self.search_btn = QPushButton("Rezepte suchen")
        self.search_btn.clicked.connect(self.handle_search)
        nav.addWidget(self.search_btn)

        root.addLayout(nav)
        self.setLayout(root)

        self.load_from_state()

    def _toggle_intolerances(self) -> None:
        visible = self.intol_toggle_btn.isChecked()
        self.intol_container.setVisible(visible)
        self.intol_toggle_btn.setText("Hide" if visible else "Show")

    def _toggle_time_limit(self) -> None:
        enabled = self.time_enabled.isChecked()
        self.time_slider.setEnabled(enabled)

    def load_from_state(self) -> None:
        prefs = self.state.preferences

        # diet
        if prefs.diet in DIETS:
            self.diet_combo.setCurrentIndex(DIETS.index(prefs.diet))
        else:
            self.diet_combo.setCurrentIndex(0)

        # cuisine
        if prefs.cuisine in CUISINES:
            self.cuisine_combo.setCurrentIndex(CUISINES.index(prefs.cuisine))
        else:
            self.cuisine_combo.setCurrentIndex(0)

        # intolerances
        for cb in self.intolerance_boxes:
            cb.setChecked(cb.text() in prefs.intolerances)

        # sort
        if prefs.sort_mode in SORT_MODES:
            self.sort_combo.setCurrentText(prefs.sort_mode)
        else:
            self.sort_combo.setCurrentText("popularity")

        # number
        self.number_spin.setValue(prefs.number)

        # time limit
        if prefs.max_ready_time is not None:
            self.time_enabled.setChecked(True)
            self.time_slider.setEnabled(True)
            self.time_slider.setValue(prefs.max_ready_time)
            self.time_label.setText(f"{prefs.max_ready_time} minutes")
        else:
            self.time_enabled.setChecked(False)
            self.time_slider.setEnabled(False)
            self.time_label.setText(f"{self.time_slider.value()} minutes")

    def handle_search(self) -> None:
        try:
            self.search_btn.setEnabled(False)
            self.search_btn.setText("Searching...")

            # write prefs back to state
            self.state.preferences.diet = self.diet_combo.currentData()
            self.state.preferences.cuisine = self.cuisine_combo.currentData()
            self.state.preferences.sort_mode = self.sort_combo.currentText()
            self.state.preferences.number = self.number_spin.value()

            # time limit optional
            if self.time_enabled.isChecked():
                self.state.preferences.max_ready_time = self.time_slider.value()
            else:
                self.state.preferences.max_ready_time = None

            # intolerances
            self.state.preferences.intolerances = [
                cb.text() for cb in self.intolerance_boxes if cb.isChecked()
            ]

            recipes = self.recipe_service.search_recipes(
                self.state.ingredients,
                self.state.preferences,
            )
            self.state.recipes = recipes

            if not recipes:
                QMessageBox.information(self, "No results", "No recipes found for these preferences.")
                return

            self.on_next()

        except Exception as e:
            QMessageBox.critical(self, "Search failed", str(e))
        finally:
            self.search_btn.setEnabled(True)
            self.search_btn.setText("Rezepte suchen")
