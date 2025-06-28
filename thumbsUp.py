import cv2
import mediapipe as mp

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)

# Open webcam
cap = cv2.VideoCapture(0)

def is_thumbs_up(hand_landmarks):
    """
    Basic logic to detect thumbs-up:
    - Thumb is extended (tip above MCP joint)
    - Other fingers are folded (tip below PIP joint)
    """
    landmarks = hand_landmarks.landmark

    # Indices of relevant landmarks
    thumb_tip = landmarks[4]
    thumb_mcp = landmarks[2]

    # Other fingers: index, middle, ring, pinky
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]

    # Check thumb is up (Y decreases upward in image)
    thumb_up = thumb_tip.y < thumb_mcp.y

    # Check all other fingers are down
    fingers_folded = all(landmarks[tip].y > landmarks[pip].y
                         for tip, pip in zip(finger_tips, finger_pips))

    return thumb_up and fingers_folded

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip and convert to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if is_thumbs_up(hand_landmarks):
                cv2.putText(frame, '👍 Thumbs Up Detected!', (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Thumbs Up Detector', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release and cleanup
cap.release()
cv2.destroyAllWindows()
