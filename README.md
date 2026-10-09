# Foody 🍽️

Foody recognizes food ingredients live through your webcam and then suggests recipes you can cook with them.

## Demovideo

Eine kurze Demo der App. Klick auf das Bild, um das Video auf YouTube zu öffnen.

<p align="center">
  <a href="https://youtu.be/jfQ2PmrezOE">
    <img src="https://img.youtube.com/vi/jfQ2PmrezOE/maxresdefault.jpg" alt="Foody-Demovideo auf YouTube ansehen" width="720">
  </a>
  <br>
  <a href="https://youtu.be/jfQ2PmrezOE"><b>▶ Video auf YouTube ansehen</b></a>
</p>

---

## How it works

1. **Detect.** A custom-trained YOLO model (Ultralytics) watches the webcam feed and collects every ingredient it sees.
2. **Cook.** When you press `q`, the list of detected ingredients is sent to Google Gemini, which returns three recipe ideas.

The model recognizes **19 ingredients**:
apple, beef, bell pepper, bread, broccoli, carrot, chicken, chili pepper, egg, garlic, lemon, lettuce, mushroom, onion, orange, potato, rice, salmon, tomato.

## Getting started

```bash
pip install ultralytics opencv-python google-genai
```

Set your Gemini API key as an environment variable (`GEMINI_API_KEY`), then run:

```bash
python main.py
```

Press `q` in the camera window to stop detecting and get your recipes.

## Project structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point: runs detection, then recipe generation |
| `detector.py` | Live webcam detection (model path, camera index and thresholds are set at the top) |
| `gemini_api.py` | Builds the prompt and asks Gemini for recipes |
| `train.py` / `trainV2multiOptimizatio.py` | Model training scripts |
| `valid.py`, `test*.py`, `liveTest.py`, `enzelbilderTest.py` | Evaluation and testing on images and live video |

## Dataset & training

The dataset was curated and labeled on Roboflow
([less-igredients](https://universe.roboflow.com/foody-8k61y/less-igredients/dataset/2), CC BY 4.0).
Models were trained with YOLO11 and YOLO26 at 640px using AdamW and on-the-fly augmentation (mosaic, mixup, HSV, flips).

## Team

- **Leon Kuvecke**: main app programmer (detection app, Gemini recipe integration)
- **xxPigelxx**: model training and dataset curation
