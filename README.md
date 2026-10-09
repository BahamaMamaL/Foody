# Foody 🍽️

**Real-time ingredient recognition with computer vision.** Point your webcam at the food you have, and Foody detects the ingredients, finds matching recipes and answers your questions about them.

Built as a university project for the course *Adaptive Systems and Artificial Intelligence* in the Media Systems program at HAW Hamburg.

## Demo video

A short demo of the app. Click the image to watch it on YouTube.

<p align="center">
  <a href="https://youtu.be/jfQ2PmrezOE">
    <img src="https://img.youtube.com/vi/jfQ2PmrezOE/maxresdefault.jpg" alt="Watch the Foody demo on YouTube" width="720">
  </a>
  <br>
  <a href="https://youtu.be/jfQ2PmrezOE"><b>▶ Watch on YouTube</b></a>
</p>

---

## How it works

1. **Scan.** A live webcam preview shows YOLO detections in real time. Press *Weiter* to take a snapshot of the detected ingredients.
2. **Review.** Add or remove ingredients manually.
3. **Filter.** Set diet, intolerances, cuisine, max. ready time and sorting.
4. **Find recipes.** Matching recipes are fetched from the [Spoonacular API](https://spoonacular.com/food-api).
5. **Cook & ask.** Open a recipe to see ingredients and instructions, and ask the built-in assistant (Google Gemini 2.5 Flash) for substitutions or tips. It gets the recipe as context.

The model recognizes **19 ingredients**:
apple, beef, bell pepper, bread, broccoli, carrot, chicken, chili pepper, egg, garlic, lemon, lettuce, mushroom, onion, orange, potato, rice, salmon, tomato.

## Tech stack

- **Python** with **PySide (Qt)** for the desktop UI
- **Ultralytics YOLO26s** for object detection, running locally (inference in a separate worker thread so the UI stays smooth)
- **OpenCV** for the webcam stream
- **Spoonacular API** for recipe data
- **Google Gemini 2.5 Flash** for the recipe chat

## Results

Evaluated on the Foody test set:

| Model | mAP50 | mAP50-95 | Precision | Recall |
|-------|-------|----------|-----------|--------|
| YOLO11s | 0.935 | 0.789 | 0.874 | 0.889 |
| **YOLO26s** (used in the app) | 0.933 | 0.790 | 0.891 | 0.871 |

Live performance (webcam, ONNX, full pipeline):

| Model | CPU (Ryzen 7 5800X) | GPU (RTX 2070 Super) |
|-------|---------------------|----------------------|
| YOLO11s | 11.4 FPS | 38.0 FPS |
| **YOLO26s** | 13.3 FPS | 41.6 FPS |

YOLO26s was chosen for the app. Its NMS-free head avoids the duplicate and suppressed boxes YOLO11 showed in live use, and it confuses classes slightly less often.

> **Note:** The test set is similar to the training data, so real-world accuracy is lower than these numbers suggest. Small, distant, partly hidden or motion-blurred ingredients are the main weak spots.

## Dataset & training

- **21,109 images, 19 classes**, merged and relabeled from several Roboflow Universe datasets (similar subclasses like red/green/yellow pepper were merged into one class)
- Split: 16,379 train / 2,995 validation / 1,735 test
- Dataset: [Foody Dataset on Roboflow Universe](https://universe.roboflow.com/foody-8k61y/foody-dataset-qtti0)

Training setup: fine-tuned from COCO-pretrained weights, 640×640 input, batch size 8, up to 100 epochs (patience 30), AdamW. Augmentation: mosaic (1.0), mixup (0.1), HSV shifts, translation, scaling and horizontal flips. Because the dataset mostly contains single-ingredient images, mosaic was essential for multi-ingredient detection.

## Getting started

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

Set your API keys as environment variables:

```bash
export GEMINI_API_KEY="your-key"
export SPOONACULAR_API_KEY="your-key"
```

Then run:

```bash
python main.py
```

## Team

- **[Leon Kuvecke](https://github.com/BahamaMamaL)**: app development. Built the PySide desktop app with live YOLO preview (threaded inference), the ingredient review and filter flow, the Spoonacular recipe search and the Gemini recipe chat
- **[Nikolai Bohse](https://github.com/xxPigelxx)**: dataset & model. Merged and relabeled 21k images from multiple sources, reduced the class set from 40 to 19, trained and tuned YOLO11s/YOLO26s, ran the evaluation and benchmarks
