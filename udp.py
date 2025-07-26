# Referencing Hand Tracking & sending to Unity https://www.youtube.com/watch?v=RQ-2JWzNc6k&t=498s
# CVZone Hand Tracking https://github.com/cvzone/cvzone/blob/master/cvzone/HandTrackingModule.py
# Unity (server) must be running first.

import socket
import cv2
from cvzone.HandTrackingModule import HandDetector
from deepface import DeepFace
import mediapipe
import time

cap = cv2.VideoCapture(0)

# Hand Detector
detector = HandDetector(maxHands=1, detectionCon=0.8)
# This will be turned true if a thumb is detected, and
# after an emotion video has played, it will go back to false
thumbDetected = False

# How many seconds to detect the same emotion
# before playing the video
emotionThreshold = 1.0
# Used to timeout if a thumb is detected but no emotion
startTimeout = None
currEmotion = None

# Check if Unity is playing one of the emotion clips 
# before continuing the script
readyToSendData = True

# Communication UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5505)

def isThumbsUp(hand):
    # Basic logic to detect thumbs-up:
    # Thumb is extended (tip above MCP joint)
    # Other fingers are folded (tip below PIP joint)   
    lm = hand["lmList"]  # list of 21 (x, y, z) = [0], [1], [2]

    if not lm or len(lm) != 21:
        print("ERROR: Hand not properly detected.")
        return False

    # Indices of thumb landmarks
    thumb_tip = lm[4]
    thumb_mcp = lm[2]

    # Other fingers: index, middle, ring, pinky
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]

    # Check thumb is up (Y decreases upward in image)
    thumb_up = thumb_tip[2] < thumb_mcp[2]
    thumb_up1 = thumb_tip[1] < thumb_mcp[1]

    # Check all other fingers are down
    fingers_folded = all(lm[tip][2] > lm[pip][2]
                         for tip, pip in zip(finger_tips, finger_pips))
    fingers_folded1 = all(lm[tip][1] > lm[pip][1]
                         for tip, pip in zip(finger_tips, finger_pips))

    return (thumb_up or thumb_up1) and (fingers_folded or fingers_folded1)

while True:
    while not readyToSendData:
        try:
            message, addr = sock.recvfrom(2)
        except Exception as e:
            print(f"Error receiving data: {e}")

        if message:
            message_value = message[0]
            if message_value == 7:
                print("Clip finished playing.")
                readyToSendData = True
                message = 0

    success, webcam = cap.read()
    if not success:
        print("ERROR: Problem with webcam.")

    # Hand information
    hands, webcam = detector.findHands(webcam)

    if hands:
        hand = hands[0]
        #isThumbsUpDebug(hand)
        if isThumbsUp(hand):
            thumbDetected = True
            startTimeout = time.time()
            print("Thumbs up.")

    if thumbDetected:
        if time.time() - startTimeout > 10.0:
            print("timed out.")
            thumbDetected = False
            continue
        try:
            # Deepface model to analyze facial expression
            # For detector_backend, I use 'ssd' which has worked best for me
            # as far as needed speed and accuracy. 
            analysis = DeepFace.analyze(webcam, actions=['emotion'], enforce_detection=True, detector_backend='ssd')
            emotion = analysis[0]['dominant_emotion']
            
            if emotion is not None:
                # Check length of emotion expressed
                if emotion != currEmotion:
                    currEmotion = emotion
                    startTime = time.time()
                else:
                    cv2.putText(webcam, emotion, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2, cv2.LINE_AA)
                    elapsed = time.time() - startTime

                    if elapsed >= emotionThreshold:
                        print(f"Emotion '{emotion}' detected for {emotionThreshold} seconds.")
                        # detect emotion
                        if emotion == "happy":
                            print("happy")
                            readyToSendData = False
                            sock.sendto(str.encode(str("happyClips")), serverAddressPort)
                            thumbDetected = False
                            continue
                        elif emotion == "sad":
                            print("sad")
                            readyToSendData = False
                            sock.sendto(str.encode(str("sadClips")), serverAddressPort)
                            thumbDetected = False
                            continue
                        elif emotion == "angry":
                            print("angry")
                            readyToSendData = False
                            sock.sendto(str.encode(str("angryClips")), serverAddressPort)
                            thumbDetected = False
                            continue

        except ValueError:
            # print("No face currently detected.") # for debugging
            # if a face isn't detected, just continue.
            # the exception handler is necessary, otherwise the
            # program will crash.
            continue

    cv2.imshow("Webcam", webcam)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
socket.close()