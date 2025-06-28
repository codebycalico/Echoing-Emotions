from deepface import DeepFace
import cv2
import time
import mediapipe as mp

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)

# Video paths
MAIN_VID = "videos\main.mp4"
SAMPLE_VID = "videos\sample.mp4"

# Timer variables
currEmotion = None
startTime = None
# How many seconds to detect the same emotion
# before playing the video
emotionThreshold = 3
# This will be turned true if a thumb is detected, and
# after an emotion video has played, it will go back to
# false
thumbActivation = False

def is_thumbs_up(hand_landmarks):
    #Basic logic to detect thumbs-up:
    # Thumb is extended (tip above MCP joint)
    # Other fingers are folded (tip below PIP joint)

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

def play_sample_video():
    print("Emotion held for threshold time.")
    sample = cv2.VideoCapture(SAMPLE_VID)
    if not sample.isOpened():
        print("Error opening video.")
        return

    while sample.isOpened():
        _, sample_frame = sample.read()
        if not _:
            break
        cv2.imshow("Sample video", sample_frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    sample.release()
    cv2.destroyWindow("Sample video")


# Webcam
cap = cv2.VideoCapture(0)
# Main video
mainCap = cv2.VideoCapture(MAIN_VID)

while True:
    ret, frame = cap.read()
    mainRet, mainFrame = mainCap.read()
    if not ret:
        print("Problem with webcam.")
        break
    if not mainRet:
        print("End of video reached.")
        mainCap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
    
    # flip webcam video and convert to RGB
    # for mediapipe
    frame = cv2.flip(frame, 1)
    mp_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # results of hand detection
    result = hands.process(mp_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            if is_thumbs_up(hand_landmarks):
                cv2.putText(mainFrame, 'Emotion detection started...', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2, cv2.LINE_AA )
                thumbActivation = True

    print(thumbActivation)
    if thumbActivation:
        try:
            # Deepface model to analyze facial expression
            # For detector_backend, I use 'ssd' which has worked best for me
            # as far as needed speed and accuracy. 
            analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=True, detector_backend='ssd')
            emotion = analysis[0]['dominant_emotion']
            
            if emotion is not "neutral":
                # Check length of emotion expressed
                if emotion != currEmotion:
                    currEmotion = emotion
                    startTime = time.time()
                else:
                    cv2.putText(mainFrame, emotion, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2, cv2.LINE_AA)
                    elapsed = time.time() - startTime
                    if elapsed >= emotionThreshold:
                        print(f"Emotion '{emotion}' detected for {emotionThreshold} seconds. Playing video...")
                        # start video
                        thumbActivation = False
                        play_sample_video()
                        startTime = time.time()

        except ValueError:
            print("No face currently detected.")

    cv2.imshow("DeepFace Emotion Detection Over Video", mainFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
mainCap.release()
cv2.destroyAllWindows()