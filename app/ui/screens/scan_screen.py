from __future__ import annotations

import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QMessageBox,
    QHBoxLayout,
)

from app.state.app_state import AppState
from app.services.detection_service import DetectionService
from app.services.ingredient_service import IngredientService


class ScanScreen(QWidget):
    def __init__(
        self,
        state: AppState,
        detection_service: DetectionService,
        ingredient_service: IngredientService,
        on_next,
        camera_index: int = 0,
    ) -> None:
        super().__init__()
        self.state = state
        self.detection_service = detection_service
        self.ingredient_service = ingredient_service
        self.on_next = on_next

        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Camera not available (index={camera_index})")

        self.current_frame = None

        # --- UI ---
        root = QVBoxLayout()

        title = QLabel("Scan ingredients (Live preview + Snapshot scan)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        root.addWidget(title)

        # Preview + list side-by-side
        row = QHBoxLayout()

        self.preview = QLabel("Camera preview")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(360)
        self.preview.setStyleSheet("background: #111; color: #ccc;")
        row.addWidget(self.preview, 2)

        right = QVBoxLayout()
        right.addWidget(QLabel("Detected ingredients:"))
        self.list_widget = QListWidget()
        right.addWidget(self.list_widget, 1)
        row.addLayout(right, 1)

        root.addLayout(row)

        self.scan_btn = QPushButton("Scan (use current frame)")
        self.scan_btn.clicked.connect(self.handle_scan)
        root.addWidget(self.scan_btn)

        self.next_btn = QPushButton("Weiter")
        # Allow skipping scan even if nothing detected
        self.next_btn.setEnabled(True)
        self.next_btn.clicked.connect(self.handle_next)
        root.addWidget(self.next_btn)

        self.setLayout(root)

        # --- Timer for live preview ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_preview)
        self.timer.start(30)  # ~33 FPS preview target (actual depends on machine)

        self.refresh()

    def handle_next(self) -> None:
        # Optional UX hint (non-blocking)
        if len(self.state.ingredients) == 0:
            QMessageBox.information(
                self,
                "No ingredients detected",
                "No ingredients were detected. You can add ingredients manually on the next screen.",
            )
        self.on_next()

    def refresh(self) -> None:
        self.list_widget.clear()
        for item in self.state.ingredients:
            self.list_widget.addItem(f"{item.name_raw} ({item.source})")

        # Always allow Next (skip supported)
        self.next_btn.setEnabled(True)

    def _update_preview(self) -> None:
        ok, frame = self.cap.read()
        if not ok or frame is None:
            return

        self.current_frame = frame

        # Convert BGR (OpenCV) -> RGB (Qt)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Scale to fit label
        pix = QPixmap.fromImage(qimg).scaled(
            self.preview.width(),
            self.preview.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.preview.setPixmap(pix)

    def handle_scan(self) -> None:
        try:
            if self.current_frame is None:
                QMessageBox.warning(self, "No frame", "No camera frame available yet.")
                return

            self.scan_btn.setEnabled(False)
            self.scan_btn.setText("Scanning...")

            detected = self.detection_service.detect_on_frame(self.current_frame)
            self.ingredient_service.merge_detection(self.state, detected)
            self.refresh()

        except Exception as e:
            QMessageBox.critical(self, "Scan failed", str(e))
        finally:
            self.scan_btn.setEnabled(True)
            self.scan_btn.setText("Scan (use current frame)")

    def closeEvent(self, event) -> None:
        # Clean up camera resources when widget is closed
        try:
            self.timer.stop()
        except Exception:
            pass
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass
        super().closeEvent(event)
