from pathlib import Path
from app.services.detection_service import DetectionService

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "best.pt"
print("Using model path:", MODEL_PATH)

print("Creating DetectionService...")
svc = DetectionService(
    model_path=str(MODEL_PATH),
    camera_index=0,
    confidence_threshold=0.5,
)
print("DetectionService created. Running detect_once...")

frame, detected = svc.detect_once()

print("detect_once finished.")
print("Detected ingredients:", [d.name_raw for d in detected])
print("Count:", len(detected))
print("Frame type:", type(frame))
