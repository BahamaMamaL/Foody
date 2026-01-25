import os
import threading
import time
import cv2
import sys

# --- EINSTELLUNGEN ---
MODEL_FILENAME = "yolo11final.onnx"
CAMERA_ID = 0
DURATION = 60

# WICHTIG: Hier steuern wir den Test-Modus
# True  = Erzwingt CPU (versteckt die GPU vor dem Programm)
# False = Nutzt GPU (wenn verfügbar und installiert)
FORCE_CPU_TEST = False
# ---------------------

# 1. GPU VOR ALLEN ANDEREN IMPORTS DEAKTIVIEREN
if FORCE_CPU_TEST:
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    print(">>> MODUS: CPU ERZWINGEN (GPU deaktiviert)")
else:
    print(">>> MODUS: GPU ERLAUBT (System-Standard)")

# Jetzt erst die schweren Imports laden
import torch
from ultralytics import YOLO

# Global vars für Threading
latest_frame = None
keep_running = True


def camera_thread():
    """Liest Kamerabilder im Hintergrund so schnell wie möglich."""
    global latest_frame, keep_running
    cap = cv2.VideoCapture(CAMERA_ID)

    # Kamera optimieren (optional)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("[Fehler] Kamera nicht gefunden.")
        keep_running = False
        return

    while keep_running:
        ret, frame = cap.read()
        if ret:
            latest_frame = frame
        else:
            keep_running = False
            break
    cap.release()


def benchmark_final():
    global latest_frame, keep_running

    # 1. Pfad finden
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, MODEL_FILENAME)

    print("-" * 40)
    print(f"Test-Dauer: {DURATION} Sekunden")
    print(f"Modell:     {MODEL_FILENAME}")

    if not os.path.exists(model_path):
        print(f"[FEHLER] Datei nicht gefunden in: {script_dir}")
        return

    # 2. Modell laden
    print("Lade Modell...")
    try:
        # Bei ONNX task='detect' angeben
        model = YOLO(model_path, task='detect')

        # DEBUG: Prüfen, worauf ONNX wirklich läuft
        if MODEL_FILENAME.endswith(".onnx"):
            import onnxruntime as ort
            print(f"Aktive ONNX Provider: {ort.get_available_providers()}")

    except Exception as e:
        print(f"[CRASH] Fehler beim Laden: {e}")
        return

    # 3. Kamera Thread starten
    print("Starte Kamera-Thread...")
    t = threading.Thread(target=camera_thread)
    t.start()

    # Warten auf erstes Bild
    while latest_frame is None and keep_running:
        time.sleep(0.01)

    print("START MESSUNG (High-Speed Loop)...")

    frame_count = 0
    start_time = time.time()

    # Anzeige aktivieren? (Kostet etwas Leistung, ist aber cool)
    SHOW_WINDOW = True

    while True:
        now = time.time()
        if (now - start_time) >= DURATION:
            break
        if not keep_running:
            break

        # Bild holen (Kopie, damit Threading sicher ist)
        if latest_frame is None:
            continue
        img = latest_frame.copy()

        # INFERENZ
        # verbose=False ist wichtig für Speed
        results = model(img, verbose=False)

        frame_count += 1

        # Visualisierung
        if SHOW_WINDOW:
            annotated = results[0].plot()

            # FPS & MS Berechnung (Live)
            elapsed = now - start_time
            if elapsed > 0:
                current_avg_fps = frame_count / elapsed
                current_avg_ms = 1000 / current_avg_fps  # Umrechnung FPS -> ms
            else:
                current_avg_fps = 0
                current_avg_ms = 0

            # Text: FPS
            cv2.putText(annotated, f"FPS: {int(current_avg_fps)}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Text: Millisekunden (Neu!)
            cv2.putText(annotated, f"Lat: {current_avg_ms:.1f} ms", (20, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # Text: Modus
            cv2.putText(annotated, f"Mode: {'CPU' if FORCE_CPU_TEST else 'GPU'}", (20, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            cv2.imshow("Benchmark", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # CLEANUP
    keep_running = False
    t.join()
    cv2.destroyAllWindows()

    # ERGEBNISSE
    total_time = time.time() - start_time
    avg_fps = frame_count / total_time
    avg_ms = 1000 / avg_fps if avg_fps > 0 else 0

    print("\n" + "=" * 40)
    print("BENCHMARK ERGEBNIS:")
    print(f"Modus:          {'CPU (Erzwungen)' if FORCE_CPU_TEST else 'GPU (Erlaubt)'}")
    print(f"Frames Gesamt:  {frame_count}")
    print(f"Zeit Gesamt:    {total_time:.2f} s")
    print(f"DURCHSCHNITT:   {avg_fps:.2f} FPS | {avg_ms:.2f} ms")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    benchmark_final()
