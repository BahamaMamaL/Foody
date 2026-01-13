# app/services/detection_service.py

from __future__ import annotations

from typing import List, Tuple

from ultralytics import YOLO

from app.domain.models import RecognizedIngredient


class DetectionService:
    def __init__(
        self,
        model_path: str,
        camera_index: int = 0,
        confidence_threshold: float = 0.6,
    ) -> None:
        self.camera_index = camera_index
        self.confidence_threshold = confidence_threshold

        try:
            self.model = YOLO(model_path)
        except Exception as e:
            raise RuntimeError(f"Model load failed: {e}") from e

    def detect_on_frame(self, frame) -> List[RecognizedIngredient]:
        """
        YOLO inference auf einem bestehenden Frame (numpy array).
        Gibt nur die Detektionen zurück (keine Annotation).
        """
        try:
            results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
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
        """
        YOLO inference + annotated frame (mit Boxes/Labels).
        Returns:
          annotated_frame (BGR numpy array)
          detected: List[RecognizedIngredient]
        """
        try:
            results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
        except Exception as e:
            raise RuntimeError(f"YOLO inference failed: {e}") from e

        annotated = results[0].plot() if results else frame

        detected: List[RecognizedIngredient] = []
        for r in results:
            for box in getattr(r, "boxes", []):
                cls = int(box.cls[0])
                name = self.model.names.get(cls, str(cls))
                conf = float(box.conf[0]) if box.conf is not None else None
                detected.append(RecognizedIngredient(name_raw=name, confidence=conf))

        return annotated, detected
