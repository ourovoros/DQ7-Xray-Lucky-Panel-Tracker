import cv2
import numpy as np
import time
from collections import deque

# --- Device Configuration ---
DEVICE_ID = 1
cap = cv2.VideoCapture(DEVICE_ID, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# --- Tuning Parameters ---
SWAP_COOLDOWN = 0.6  # Minimum interval between swaps (seconds)
CONFIRM_FRAMES = 2  # Frames required to confirm "Face-Up" state
SAT_THRESHOLD = 85  # Saturation threshold (lower = more likely to be "Face-Up")
ALPHA = 0.2  # Blending ratio: 0.2 live / 0.8 template (high transparency)

# --- State Management Variables ---
fixed_rois = []  # List of panel coordinates [(x, y, w, h), ...]
panel_contents = {}  # Mapping of index to ID (e.g., {0: "P1", ...})
panel_images = {}  # Mapping of index to initial captured images
panel_history = {}  # Buffer for frame-by-frame face-up detection
current_difficulty = "None"

swap_locked = False
last_swap_time = 0


def detect_panels_auto(frame):
    """
    Detects white panels in the frame and determines difficulty by count.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Filter based on expected area size of DQ7 Lucky Panel cards
        if 4000 < w * h < 25000:
            detected.append((x, y, w, h))

    # Sort detected panels from top-left to bottom-right
    detected.sort(key=lambda b: (b[1] // 50, b[0]))

    count = len(detected)
    diff = "Unknown"
    if count == 12:
        diff = "Beginner (3x4)"
    elif count == 16:
        diff = "Intermediate (4x4)"
    elif count == 20:
        diff = "Advanced (4x5)"
    return detected, diff


def is_face_up_robust(roi):
    """
    Determines if a panel is 'Face-Up' using Saturation and Value (Brightness).
    """
    if roi.size == 0: return False
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    avg_sat = np.mean(hsv[:, :, 1])
    avg_val = np.mean(hsv[:, :, 2])

    # Face-up is typically low saturation and high brightness (white/grayish)
    return avg_sat < SAT_THRESHOLD and avg_val > 100


print("--- DQ7 Lucky Panel Tracker (Overlay & Auto-Detect) ---")
print("Press 'S' during the initial 'All Reveal' screen to save panel images.")

while True:
    ret, frame = cap.read()
    if not ret: break
    display_frame = frame.copy()
    current_active_indices = []

    if not fixed_rois:
        # --- Preview Mode ---
        temp_rois, diff_pred = detect_panels_auto(frame)
        for (x, y, w, h) in temp_rois:
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (255, 255, 255), 1)
        cv2.putText(display_frame, f"Detected: {len(temp_rois)} -> {diff_pred}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    else:
        # --- Fixed Mode ---
        for i, (x, y, w, h) in enumerate(fixed_rois):
            roi = frame[y:y + h, x:x + w]

            # Stabilization (Debouncing)
            is_up_now = is_face_up_robust(roi)
            if i not in panel_history:
                panel_history[i] = deque(maxlen=CONFIRM_FRAMES)
            panel_history[i].append(is_up_now)

            is_confirmed_up = all(panel_history[i]) and len(panel_history[i]) == CONFIRM_FRAMES

            # Overlay Processing
            if i in panel_images:
                template = panel_images[i]
                if template.shape[:2] != (h, w):
                    template = cv2.resize(template, (w, h))

                # Blend live footage with the saved template
                # display = live * ALPHA + template * (1 - ALPHA)
                blended_roi = cv2.addWeighted(roi, ALPHA, template, 1 - ALPHA, 0)
                display_frame[y:y + h, x:x + w] = blended_roi

            # Rendering
            color = (0, 255, 0) if is_confirmed_up else (255, 0, 0)  # Green = Face-Up, Blue = Face-Down
            if is_confirmed_up:
                current_active_indices.append(i)

            cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(display_frame, str(panel_contents[i]), (x + 5, y + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.putText(display_frame, f"Mode: {current_difficulty}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # --- Swap Detection Logic ---
    curr_set = set(current_active_indices)
    now = time.time()

    # If exactly 2 panels are flipped and cooldown has passed
    if len(curr_set) == 2:
        if not swap_locked and (now - last_swap_time > SWAP_COOLDOWN):
            idx1, idx2 = list(curr_set)

            # Swap content IDs and corresponding overlay images
            panel_contents[idx1], panel_contents[idx2] = panel_contents[idx2], panel_contents[idx1]
            panel_images[idx1], panel_images[idx2] = panel_images[idx2], panel_images[idx1]

            print(f"Swap Triggered: {panel_contents[idx1]} <-> {panel_contents[idx2]}")

            swap_locked = True
            last_swap_time = now
            # Clear history to prevent multiple triggers in one movement
            for h_buf in panel_history.values(): h_buf.clear()

    elif len(curr_set) == 0:
        # Reset lock once all panels are face-down
        swap_locked = False

    cv2.imshow("DQ7 Lucky Panel Tracker", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        # Save coordinates, IDs, and panel images for overlay
        fixed_rois, current_difficulty = detect_panels_auto(frame)
        panel_contents = {i: f"P{i + 1}" for i in range(len(fixed_rois))}
        panel_images = {i: frame[y:y + h, x:x + w].copy() for i, (x, y, w, h) in enumerate(fixed_rois)}
        panel_history = {i: deque(maxlen=CONFIRM_FRAMES) for i in range(len(fixed_rois))}
        print(f"Locked: {current_difficulty} ({len(fixed_rois)} panels)")

    if key == ord('r'):
        fixed_rois = []
        print("Reset to Preview Mode.")

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()