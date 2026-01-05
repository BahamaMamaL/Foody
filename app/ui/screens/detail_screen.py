from __future__ import annotations

import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QMessageBox,
)

from app.state.app_state import AppState
from app.services.chat_service import ChatService
from app.domain.models import ChatMessage


class DetailScreen(QWidget):
    def __init__(
        self,
        state: AppState,
        chat_service: ChatService,
        on_back,
    ) -> None:
        super().__init__()
        self.state = state
        self.chat_service = chat_service
        self.on_back = on_back

        # simple in-memory cache: url -> QPixmap
        self._image_cache: dict[str, QPixmap] = {}

        root = QVBoxLayout()

        # Top bar
        top = QHBoxLayout()
        back_btn = QPushButton("Zurück")
        back_btn.clicked.connect(self.on_back)
        top.addWidget(back_btn)

        self.title_label = QLabel("Recipe")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top.addWidget(self.title_label, 1)

        root.addLayout(top)

        # --- Image (left) + Ingredients (right) ---
        header_row = QHBoxLayout()

        self.image_label = QLabel("No image")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedWidth(360)
        self.image_label.setMinimumHeight(240)
        self.image_label.setStyleSheet("background: #111; color: #ccc;")
        header_row.addWidget(self.image_label)

        ingredients_col = QVBoxLayout()
        ing_title = QLabel("Ingredients")
        ing_title.setStyleSheet("font-weight: bold;")
        ingredients_col.addWidget(ing_title)

        self.ingredients_view = QTextEdit()
        self.ingredients_view.setReadOnly(True)
        ingredients_col.addWidget(self.ingredients_view, 1)

        header_row.addLayout(ingredients_col, 1)
        root.addLayout(header_row)

        # Instructions
        instr_title = QLabel("Instructions")
        instr_title.setStyleSheet("font-weight: bold;")
        root.addWidget(instr_title)

        self.instructions_view = QTextEdit()
        self.instructions_view.setReadOnly(True)
        root.addWidget(self.instructions_view, 1)

        # Chat area
        chat_title = QLabel("Chat about this recipe")
        chat_title.setStyleSheet("font-weight: bold;")
        root.addWidget(chat_title)

        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setMinimumHeight(150)
        root.addWidget(self.chat_view)

        chat_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask a question…")
        chat_row.addWidget(self.chat_input, 1)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.handle_send)
        chat_row.addWidget(self.send_btn)

        root.addLayout(chat_row)

        self.setLayout(root)
        self.refresh()

    def _load_pixmap_from_url(self, url: str) -> QPixmap | None:
        if not url:
            return None
        if url in self._image_cache:
            return self._image_cache[url]

        try:
            r = requests.get(url, timeout=20)
            if r.status_code != 200:
                return None
            pix = QPixmap()
            ok = pix.loadFromData(r.content)
            if not ok:
                return None
            self._image_cache[url] = pix
            return pix
        except Exception:
            return None

    def refresh(self) -> None:
        recipe = self.state.selected_recipe
        if recipe is None:
            self.title_label.setText("No recipe selected")
            self.image_label.setText("No image")
            self.image_label.setPixmap(QPixmap())
            self.ingredients_view.setText("")
            self.instructions_view.setText("")
            self.chat_view.setText("")
            return

        self.title_label.setText(recipe.title)

        # Image
        if recipe.image:
            pix = self._load_pixmap_from_url(recipe.image)
            if pix is not None and not pix.isNull():
                scaled = pix.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled)
                self.image_label.setText("")
            else:
                self.image_label.setPixmap(QPixmap())
                self.image_label.setText("Image failed to load")
        else:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("No image")

        # Ingredients right column
        ingredients_block = "\n".join(f"• {x}" for x in recipe.ingredients)
        self.ingredients_view.setText(ingredients_block)

        # Instructions below
        self.instructions_view.setText(recipe.instructions)

        self._render_chat()

    def _render_chat(self) -> None:
        lines = []
        for msg in self.state.chat_messages:
            who = "You" if msg.role == "user" else "Assistant"
            lines.append(f"{who}: {msg.text}")
        self.chat_view.setText("\n\n".join(lines))
        self.chat_view.verticalScrollBar().setValue(self.chat_view.verticalScrollBar().maximum())

    def handle_send(self) -> None:
        recipe = self.state.selected_recipe
        if recipe is None:
            QMessageBox.warning(self, "No recipe", "No recipe selected.")
            return

        question = self.chat_input.text().strip()
        if not question:
            return

        try:
            self.send_btn.setEnabled(False)
            self.send_btn.setText("Sending...")

            self.state.chat_messages.append(ChatMessage(role="user", text=question))
            self.chat_input.clear()
            self._render_chat()

            answer = self.chat_service.send_question(recipe, question, self.state.chat_messages)
            if answer:
                self.state.chat_messages.append(ChatMessage(role="assistant", text=answer))
            self._render_chat()

        except Exception as e:
            QMessageBox.critical(self, "Chat failed", str(e))
        finally:
            self.send_btn.setEnabled(True)
            self.send_btn.setText("Send")
