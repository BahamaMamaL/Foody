from __future__ import annotations

import cv2

from PySide6.QtCore import Qt, QTimer, QObject, QThread, Signal, Slot
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


class YoloWorker(QObject):
    """
    Läuft in eigenem QThread.
    Macht YOLO-Inferenz und schickt annotated frame + detections zurück.
    """
    preview_done = Signal(object, object)  # (annotated_frame_bgr, detected_list)
    error = Signal(str)

    def __init__(self, detection_service: DetectionService) -> None:
        super().__init__()
        self.detection_service = detection_service
        self._running = True

    @Slot(object)
    def process_preview(self, frame_bgr) -> None:
        if not self._running:
            return
        try:
            annotated, detected = self.detection_service.annotate_on_frame(frame_bgr)
            self.preview_done.emit(annotated, detected)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self) -> None:
        self._running = False


class ScanScreen(QWidget):
    """
    Live preview läuft im UI-Thread (OpenCV read + Anzeige),
    YOLO läuft im Worker-Thread, damit es flüssig bleibt.

    - Liste rechts zeigt NUR den letzten Snapshot (state.ingredients).
    - Live-Detektion wird nur intern gehalten, damit Snapshot sofort übernommen werden kann.
    """

    _preview_request = Signal(object)  # frame_bgr (queued to worker)

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

        # --- Live YOLO cache (für Snapshot) ---
        self._last_annotated_bgr = None
        self._last_detected = []
        self._preview_in_flight = False

        # --- UI ---
        root = QVBoxLayout()

        title = QLabel("Scan ingredients (YOLO Live Preview + Snapshot)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        root.addWidget(title)

        row = QHBoxLayout()

        self.preview = QLabel("Camera preview")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(360)
        self.preview.setStyleSheet("background: #111; color: #ccc;")
        row.addWidget(self.preview, 2)

        right = QVBoxLayout()
        right.addWidget(QLabel("Detected ingredients (last snapshot):"))

        # Optionaler Live-Hinweis (nur Anzahl, keine Liste überschreiben)
        self.live_hint = QLabel("Live: 0")
        self.live_hint.setStyleSheet("color: #888;")
        right.addWidget(self.live_hint)

        self.list_widget = QListWidget()
        right.addWidget(self.list_widget, 1)
        row.addLayout(right, 1)

        root.addLayout(row)

        self.scan_btn = QPushButton("Snapshot übernehmen (aktuelles Live-Bild)")
        self.scan_btn.clicked.connect(self.handle_scan)
        root.addWidget(self.scan_btn)

        self.next_btn = QPushButton("Weiter")
        self.next_btn.setEnabled(True)
        self.next_btn.clicked.connect(self.handle_next)
        root.addWidget(self.next_btn)

        self.setLayout(root)

        # --- YOLO Worker Thread Setup ---
        self.worker_thread = QThread(self)
        self.worker = YoloWorker(self.detection_service)
        self.worker.moveToThread(self.worker_thread)

        self._preview_request.connect(self.worker.process_preview, Qt.QueuedConnection)
        self.worker.preview_done.connect(self._on_preview_done, Qt.QueuedConnection)
        self.worker.error.connect(self._on_worker_error, Qt.QueuedConnection)

        self.worker_thread.start()

        # --- Timer for live preview ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_preview)
        self.timer.start(30)

        # initiale Snapshot-Liste
        self.refresh()

    # ✅ Damit MainWindow weiter self.scan_screen.refresh() aufrufen kann
    def refresh(self) -> None:
        """Extern aufgerufen beim Screen-Wechsel: zeige letzten Snapshot aus State."""
        self.refresh_snapshot_list()
        self.next_btn.setEnabled(True)

    def handle_next(self) -> None:
        if len(self.state.ingredients) == 0:
            QMessageBox.information(
                self,
                "No ingredients detected",
                "No ingredients were detected. You can add ingredients manually on the next screen.",
            )
        self.on_next()

    def refresh_snapshot_list(self) -> None:
        """Liste rechts zeigt NUR state.ingredients (letzter Snapshot)."""
        self.list_widget.clear()
        for item in self.state.ingredients:
            self.list_widget.addItem(f"{item.name_raw} ({item.source})")

    def _update_preview(self) -> None:
        ok, frame = self.cap.read()
        if not ok or frame is None:
            return

        self.current_frame = frame

        # Anzeige: annotated falls vorhanden, sonst raw
        show_bgr = self._last_annotated_bgr if self._last_annotated_bgr is not None else frame
        self._set_preview_image(show_bgr)

        # YOLO Preview anstoßen, aber nur ein Job gleichzeitig
        if not self._preview_in_flight:
            self._preview_in_flight = True
            self._preview_request.emit(frame.copy())

    def _set_preview_image(self, frame_bgr) -> None:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()

        pix = QPixmap.fromImage(qimg).scaled(
            self.preview.width(),
            self.preview.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.preview.setPixmap(pix)

    @Slot(object, object)
    def _on_preview_done(self, annotated_bgr, detected_list) -> None:
        # Cache aktualisieren (für Snapshot + Preview-Overlay)
        self._last_annotated_bgr = annotated_bgr
        self._last_detected = detected_list
        self._preview_in_flight = False

        # NICHT die Zutatenliste überschreiben!
        self.live_hint.setText(f"Live: {len(detected_list)}")

    def handle_scan(self) -> None:
        """
        Snapshot = Übernehme die LETZTE Live-Detektion in den State.
        Die Liste rechts zeigt danach den Snapshot (state.ingredients).
        """
        if not self._last_detected:
            QMessageBox.information(self, "Nothing detected", "Noch keine Zutaten erkannt.")
            return

        try:
            self.scan_btn.setEnabled(False)
            self.scan_btn.setText("Snapshot wird gespeichert...")

            # Live-Ergebnis in AppState übernehmen
            self.ingredient_service.merge_detection(self.state, self._last_detected)

            # Jetzt Liste rechts aktualisieren (Snapshot-Liste)
            self.refresh_snapshot_list()

        except Exception as e:
            QMessageBox.critical(self, "Snapshot failed", str(e))
        finally:
            self.scan_btn.setEnabled(True)
            self.scan_btn.setText("Snapshot übernehmen (aktuelles Live-Bild)")

    @Slot(str)
    def _on_worker_error(self, msg: str) -> None:
        self._preview_in_flight = False
        # bewusst kein Popup-Spam bei Preview-Fehlern

    def closeEvent(self, event) -> None:
        try:
            self.timer.stop()
        except Exception:
            pass

        try:
            self.worker.stop()
        except Exception:
            pass
        try:
            self.worker_thread.quit()
            self.worker_thread.wait(1500)
        except Exception:
            pass

        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass

        super().closeEvent(event)
