import time
import cv2
import torch
from torch.cuda import device
from ultralytics import YOLO

# --- EINSTELLUNGEN ---
MODEL_PATH = "yolo11final.pt"  # Oder 'yolo26final.pt'
IMAGE_PATHS = [
    "bild1.png",
    "bild2.png",
    "bild3.png"
]


# ---------------------

def benchmark_images():
    # Hardware prüfen
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"--- STARTE EINZELBILD-TEST auf {device.upper()} ---")

    # Modell laden
    model = YOLO(MODEL_PATH)
    model.to(device)

    # WARM-UP (Wichtig!)
    # Wir jagen ein Dummy-Bild durch, damit PyTorch bereit ist
    print("Mache Warm-up (10 Durchläufe)...")
    if len(IMAGE_PATHS) > 0:
        dummy = cv2.imread(IMAGE_PATHS[0])
        for _ in range(10):
            model(dummy, verbose=False)
    print("Warm-up fertig. Starte Messung.\n")

    print(f"{'Bild':<15} | {'Zeit (ms)':<12} | {'FPS':<10}")
    print("-" * 45)

    for img_path in IMAGE_PATHS:
        img = cv2.imread(img_path)
        if img is None:
            print(f"FEHLER: Konnte {img_path} nicht finden!")
            continue

        # Messschleife: 50x pro Bild für genauen Durchschnitt
        runs = 500
        total_time = 0

        for _ in range(runs):
            start = time.perf_counter()
            model(img, verbose=False)
            end = time.perf_counter()
            total_time += (end - start)

        avg_time_ms = (total_time / runs) * 1000
        avg_fps = 1000 / avg_time_ms

        print(f"{img_path:<15} | {avg_time_ms:<12.2f} | {avg_fps:<10.2f}")


if __name__ == "__main__":
    benchmark_images()
