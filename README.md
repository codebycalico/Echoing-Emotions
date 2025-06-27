# Mirroring Emotions
A program created with OpenCV Python to detect user emotions and then run a specified video clip based on that emotion.

## monitorEmotion.py
Using DeepFace's lightweight facial recognition analysis library for Python.

To download the required libraries, use "pip install -r requirements.txt" or you can do them one at a time.

Made using Python 3.11.0, as MediaPipe can only work with Python 3.8 - 3.11. I have only tried with 3.11.0, so I cannot testify to the other versions.

### DeepFace's analysis

#### detector_backend options
For the detector_backend option in DeepFace's emotion detection model, 'opencv' is the default option and has worked well as speed and accuracy. 'mediapipe' is fast, but not as accurate. If you want to work with 'mediapipe', note that it requires the image / video to be converted from BGR that OpenCV uses to RGB for mediapipe. 'retinaface' is supposedly the best for accuracy but requires a much slower process, so the main video that is playing becomes too choppy. For real time tasks, 'retinaface' seems unusable.
I went with using 'ssd' instead of the 'opencv' default, as opencv has had a hard time detecting the 'angry' emotion, which is important for me in this project.

#### enforce_detection option
For the enforce_detection option, True will raise an error and stop processing when no face is detected. False will bypass detection and analyze the entire image as a face, which avoids crashes, but the results can be inaccurate / meaningless as it will be guessing emotions from the video feed even if there is no face. I set it equal to True and with an exception handler, just have the program continuing. I'm not actually sure why there is an option to have it equal to false.