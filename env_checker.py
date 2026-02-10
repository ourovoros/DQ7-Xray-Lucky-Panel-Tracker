import cv2


def check_camera_environment():
    """
    Scans for available camera indices and displays previews to find the correct DEVICE_ID.
    """
    print("--- DQ7 Lucky Panel Tracker: Environment Checker ---")
    print("Scanning for available camera devices (Indices 0-10)...")

    available_indices = []

    # Check for cameras in range 0-10
    for index in range(11):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available_indices.append(index)
                cap.release()

    if not available_indices:
        print("Error: No cameras detected. Please check your USB connection.")
        return

    print(f"Found {len(available_indices)} camera(s) at index(es): {available_indices}")
    print("\nStarting previews. Press 'N' to see the next camera, or 'Q' to quit.")

    current_pos = 0
    while True:
        idx = available_indices[current_pos]
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)

        # Set common resolution for testing
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Display info on screen
            cv2.putText(frame, f"Testing DEVICE_ID: {idx}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'N' for Next Device / 'Q' to Quit", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Show resolution info
            h, w, _ = frame.shape
            cv2.putText(frame, f"Resolution: {w}x{h}", (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Environment Checker", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('n'):
                print(f"Switching from Device {idx}...")
                break
            elif key == ord('q'):
                print(f"Final Selection: DEVICE_ID = {idx}")
                cap.release()
                cv2.destroyAllWindows()
                return

        cap.release()
        current_pos = (current_pos + 1) % len(available_indices)


if __name__ == "__main__":
    check_camera_environment()