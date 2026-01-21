# app/services/detection_service.py

from __future__ import annotations

from typing import List, Tuple, Optional

import torch
from ultralytics import YOLO

from app.domain.models import RecognizedIngredient


class DetectionService:
    def __init__(
        self,
        model_path: str,
        camera_index: int = 0,
        confidence_threshold: float = 0.3,

        device: Optional[str] = None,   # <--- WICHTIG: Default auf None, damit Auto-Detect greift
    ) -> None:
        self.camera_index = camera_index
        self.confidence_threshold = confidence_threshold

        # Automatische Erkennung der Hardware
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda:0"
                # Info-Print für dich, damit du sicher bist
                print(f"✅ GPU aktiviert: {torch.cuda.get_device_name(0)}")
            else:
                self.device = "cpu"
                print("⚠️ Keine GPU gefunden (oder CUDA nicht installiert). Nutze CPU.")
        else:
            self.device = device

        try:
            self.model = YOLO(model_path)

            # Modell explizit auf die GPU schieben
            self.model.to(self.device)

        except Exception as e:
            raise RuntimeError(f"Model load failed: {e}") from e

    def _predict(self, frame):
        """Zentrale Predict-Funktion."""
        return self.model.predict(
            frame,
            conf=self.confidence_threshold,
            device=self.device,     # Nutzt "cuda:0" wenn verfügbar
            verbose=False,
            iou = 0.95
        )

    def detect_on_frame(self, frame) -> List[RecognizedIngredient]:
        try:
            results = self._predict(frame)
        except Exception as e:
            raise RuntimeError(f"YOLO inference failed: {e}") from e

        detected: List[RecognizedIngredient] = []
        for r in results:
            for box in getattr(r, "boxes", []):
                cls = int(box.cls[0])
                name = self.model.names.get(cls, str(cls))
                conf = float(box.conf[0]) if box.conf is not None else None
                detected.append(RecognizedIngredient(name_raw=name, confidence=conf))

        return detected

    def annotate_on_frame(self, frame) -> Tuple["object", List[RecognizedIngredient]]:
        try:
            results = self._predict(frame)
        except Exception as e:
            raise RuntimeError(f"YOLO inference failed: {e}") from e

        # Plot rendert das Bild mit Boxen.
        # ACHTUNG: Das Ergebnis ist ein numpy-array im BGR Format (OpenCV Standard)
        annotated = results[0].plot() if results else frame

        detected: List[RecognizedIngredient] = []
        for r in results:
            for box in getattr(r, "boxes", []):
                cls = int(box.cls[0])
                name = self.model.names.get(cls, str(cls))
                conf = float(box.conf[0]) if box.conf is not None else None
                detected.append(RecognizedIngredient(name_raw=name, confidence=conf))

        return annotated, detected
