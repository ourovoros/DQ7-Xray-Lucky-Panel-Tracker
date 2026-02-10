
---

# DQ7 Xray Lucky Panel Tracker

An OpenCV-based real-time tracking tool for the "Lucky Panel" minigame in Dragon Quest VII. This tool automatically tracks card positions during shuffle sequences and provides a semi-transparent overlay (X-ray vision) of the initial reveal.

## Features

* **Auto-Detection**: Automatically detects if you are playing on Beginner, Intermediate, or Advanced mode based on the number of panels.
* **X-Ray Overlay**: Saves images of all panels during the "all reveal" phase and overlays them back onto the cards with 80% opacity.
* **Intelligent Swap Tracking**: Tracks card movement during shuffle sequences using a robust saturation-based detection algorithm.
* **Anti-Chattering**: Implements frame-confirmation and cooldown logic to prevent double-swaps or misdetections during fast shuffles.

## Demo

Here's a quick demonstration of the tracker in action:

![DQ7 Xray Lucky Panel Tracker Demo](https://github.com/ourovoros/DQ7-Xray-Lucky-Panel-Tracker/blob/main/assets/panel_tracker_demo.gif?raw=true)

## Requirements

* Python 3.x
* OpenCV (`opencv-python`)
* NumPy

```bash
pip install opencv-python numpy

```

## How to Use

1. **Preparation**: Align your camera/capture card so the Lucky Panel board is clearly visible and centered.
2. **Initialization**: Run the script. You will see white boxes around the detected panels in "Preview Mode."
3. **Capture**: When the game reveals all panels at the start, press the **'S'** key.
* The script locks the coordinates.
* The script captures the image of each card for the overlay.
* The difficulty is automatically set (12, 16, or 20 panels).


4. **Tracking**: As the cards flip and shuffle, the tool will track the IDs (P1, P2...) and move the overlay images accordingly.
5. **Reset**: Press **'R'** to reset and return to Preview Mode for the next game.
6. **Quit**: Press **'Q'** to exit.

## Parameter Tuning

Since lighting conditions and capture quality vary, you may need to adjust the parameters at the top of the script for optimal accuracy:

| Parameter | Default | Description |
| --- | --- | --- |
| `ALPHA` | `0.2` | **Transparency**. `0.0` shows only the saved image; `1.0` shows only the live camera. `0.2` makes the "ghost" image very clear. |
| `SAT_THRESHOLD` | `85` | **Face-up detection**. Increase this (e.g., `95`) if the tool fails to detect a flipped card. Decrease it (e.g., `75`) if it misidentifies a blue card as flipped. |
| `CONFIRM_FRAMES` | `2` | **Stability**. Increase to `3` or `4` if cards are swapping randomly during movement. Higher values add slight delay but increase precision. |
| `SWAP_COOLDOWN` | `0.6` | **Speed**. The minimum time (seconds) between two swaps. Decrease this for Advanced mode if the shuffles are extremely fast. |

## Detection Logic

The tool uses the HSV color space to distinguish between the high-saturation "Blue" back of the cards and the low-saturation "White/Gray" face of the cards.

1. **Saturation (S)**: Used to detect the "Face-Up" state. Blue has high saturation; white/gray has low.
2. **Value (V)**: Used to ensure the detected area is bright enough to be a card, filtering out shadows.
3. **Debouncing**: Requires a card to be in the "Face-Up" state for `CONFIRM_FRAMES` consecutively before triggering a swap.

---

## Getting Started: Troubleshooting Your Camera

Before running the panel_overlay.py, use `env_checker.py` to identify your capture device.

1. Run the checker script:
```bash
python env_checker.py

```


2. A window will appear showing your camera feed.
3. Press **'N'** to cycle through all connected video devices (USB webcams, capture cards, etc.).
4. Note the **DEVICE_ID** shown in the top-left corner once you see your game screen.
5. Open `panel_tracker.py` and update the `DEVICE_ID` variable with your number:
```python
# Example: If env_checker.py showed index 1
DEVICE_ID = 1 

```
