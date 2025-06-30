# Horses as Emotional Mirrors
# by Calico Rose Randall

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
HAPPY_VIDEOS = ["videos\happy1.mp4", "videos\happy2.mp4", "videos\happy3.mp4", "videos\happy4.mp4",
                "videos\happy5.mp4", "videos\happy6.mp4", "videos\happy7.mp4", "videos\happy8.mp4"]
ANGRY_VIDEOS = ["videos\\angry1.mp4","videos\\angry2.mp4", "videos\\angry3.mp4", "videos\\angry4.mp4",
                "videos\\angry5.mp4"]
SAD_VIDEOS = ["videos\sad1.mp4"]

# variables to keep track of which video was played last & which to play next
# within the emotional video arrays
happyTracker = 0
angryTracker = 0
sadTracker = 0

# Timer variables
currEmotion = None
startTime = None

# How many seconds to detect the same emotion
# before playing the video
emotionThreshold = 3

# This will be turned true if a thumb is detected, and
# after an emotion video has played, it will go back to false
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

def play_happy_video():
    # variable wasn't being accessed globally without this 
    global happyTracker
    #print("Happy emotion held for threshold time.") # for debugging
    # loop through the array of video clips to play
    if happyTracker >= len(HAPPY_VIDEOS):
        happyTracker = 0

    happy = cv2.VideoCapture(HAPPY_VIDEOS[happyTracker])

    if not happy.isOpened():
        print("Error opening happy video.")
        return

    while happy.isOpened():
        _, happyFrame = happy.read()
        if not _:
            break
        cv2.putText(mainFrame, "happy, content", (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2, cv2.LINE_AA)
        
        cv2.imshow("Happy video", happyFrame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    happyTracker += 1
    happy.release()
    cv2.destroyWindow("Happy video")

def play_angry_video():
    # variable wasn't being accessed globally without this 
    global angryTracker
    #print("Angry emotion held for threshold time.") # for debugging
    # loop through the array of video clips to play
    if angryTracker >= len(ANGRY_VIDEOS):
        angryTracker = 0

    angry = cv2.VideoCapture(ANGRY_VIDEOS[angryTracker])

    if not angry.isOpened():
        print("Error opening angry video.")
        return

    while angry.isOpened():
        _, angryFrame = angry.read()
        if not _:
            break
        cv2.imshow("Angry video", angryFrame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    angryTracker += 1
    angry.release()
    cv2.destroyWindow("Angry video")

def play_sad_video():
    # variable wasn't being accessed globally without this 
    global sadTracker
    #print("Sad emotion held for threshold time.") # for debugging
    # loop through the array of video clips to play
    if sadTracker >= len(SAD_VIDEOS):
        sadTracker = 0

    sad = cv2.VideoCapture(SAD_VIDEOS[sadTracker])

    if not sad.isOpened():
        print("Error opening sad video.")
        return

    while sad.isOpened():
        _, sadFrame = sad.read()
        if not _:
            break
        cv2.imshow("Sad video", sadFrame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    
    sadTracker += 1
    sad.release()
    cv2.destroyWindow("Sad video")


# Webcam
cap = cv2.VideoCapture(0)
# Main video
mainCap = cv2.VideoCapture(MAIN_VID)

while True:
    ret, frame = cap.read()
    mainRet, mainFrame = mainCap.read()
    if not ret:
        #print("Problem with webcam.") # for debugging
        break
    if not mainRet:
        #print("End of video reached.") # for debugging
        # if the main video has reached the end, start it over
        mainCap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
    
    # flip webcam video and convert to RGB
    # for mediapipe body landmarks
    frame = cv2.flip(frame, 1)
    mp_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # results of hand detection
    result = hands.process(mp_frame)

    # parse through the hand landmarks to see if there is a thumbs up
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            if is_thumbs_up(hand_landmarks):
                cv2.putText(mainFrame, 'Emotion detection started...', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2, cv2.LINE_AA )
                thumbActivation = True

    # print(thumbActivation) # for debugging
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
                        
                        # detect emotion and start corresponding video
                        thumbActivation = False
                        if emotion == "happy":
                            play_happy_video()
                            thumbActivation = False
                        elif emotion == "sad":
                            play_sad_video()
                            thumbActivation = False
                        elif emotion == "angry":
                            play_angry_video()
                            thumbActivation = False

                        startTime = time.time()

        except ValueError:
            # print("No face currently detected.") # for debugging
            # if a face isn't detected, just continue.
            # the exception handler is necessary, otherwise the
            # program will crash.
            continue

    # Create a named window and set its property to fullscreen
    #cv2.namedWindow('DeepFace Emotion Detection Over Video', cv2.WINDOW_NORMAL)
    #cv2.setWindowProperty('DeepFace Emotion Detection Over Videor', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("DeepFace Emotion Detection Over Video", mainFrame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
mainCap.release()
cv2.destroyAllWindows()