from deepface import DeepFace
import cv2
import time

# Video paths
MAIN_VID = "videos\main.mp4"
SAMPLE_VID = "videos\sample.mp4"

# Timer variables
currEmotion = None
startTime = None
# How many seconds to detect the same emotion
# before playing the video
emotionThreshold = 3

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
    if not ret or not mainRet:
        print("A capture didn't load.")
        break

    
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
