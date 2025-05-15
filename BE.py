from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import dlib
import cv2
import keyboard
import morse_code
import constants
import threading

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def run_morse_detection(stop_event):
    print("Running Morse detection...")

    predictor_path = "D:/PROJECT/shape_predictor_68_face_landmarks.dat"
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)

    lStart, lEnd = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    rStart, rEnd = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    vs = VideoStream(src=0).start()
    total_morse = ""
    morse_word = ""
    morse_char = ""

    COUNTER = 0
    BREAK_COUNTER = 0
    EYES_OPEN_COUNTER = 0
    CLOSED_EYES = False
    WORD_PAUSE = False
    PAUSED = False

    while not stop_event.is_set():  
        frame = vs.read()
        if frame is None:
            continue
        frame = cv2.resize(frame, (450, 300))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]

            left_eye_ar = eye_aspect_ratio(leftEye)
            right_eye_ar = eye_aspect_ratio(rightEye)
            eye_ar = (left_eye_ar + right_eye_ar) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            if eye_ar < constants.EYE_AR_THRESH:
                COUNTER += 1
                BREAK_COUNTER += 1
                if COUNTER >= constants.EYE_AR_CONSEC_FRAMES:
                    CLOSED_EYES = True
                if not PAUSED:
                    morse_char = ""
                if BREAK_COUNTER >= constants.BREAK_LOOP_FRAMES:
                    break
            else:
                if BREAK_COUNTER < constants.BREAK_LOOP_FRAMES:
                    BREAK_COUNTER = 0
                EYES_OPEN_COUNTER += 1
                if COUNTER >= constants.EYE_AR_CONSEC_FRAMES_CLOSED:
                    morse_word += "-"
                    total_morse += "-"
                    morse_char += "-"
                    COUNTER = 0
                    CLOSED_EYES = False
                    PAUSED = True
                    EYES_OPEN_COUNTER = 0
                elif CLOSED_EYES:
                    morse_word += "."
                    total_morse += "."
                    morse_char += "."
                    COUNTER = 1
                    CLOSED_EYES = False
                    PAUSED = True
                    EYES_OPEN_COUNTER = 0
                elif PAUSED and EYES_OPEN_COUNTER >= constants.PAUSE_CONSEC_FRAMES:
                    morse_word += "/"
                    total_morse += "/"
                    morse_char = "/"
                    PAUSED = False
                    WORD_PAUSE = True
                    CLOSED_EYES = False
                    EYES_OPEN_COUNTER = 0
                    keyboard.write(morse_code.from_morse(morse_word))
                    morse_word = ""
                elif WORD_PAUSE and EYES_OPEN_COUNTER >= constants.WORD_PAUSE_CONSEC_FRAMES:
                    total_morse += "¦/"
                    morse_char = ""
                    WORD_PAUSE = False
                    CLOSED_EYES = False
                    EYES_OPEN_COUNTER = 0
                    keyboard.write(morse_code.from_morse("¦/"))

            cv2.putText(frame, "EAR: {:.2f}".format(eye_ar), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "{}".format(morse_char), (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            print("\033[K", "morse_word: {}".format(morse_word), end="\r")

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("]") or BREAK_COUNTER >= constants.BREAK_LOOP_FRAMES:
            keyboard.write(morse_code.from_morse(morse_word))
            break

    vs.stream.release()  
    vs.stop()  
    cv2.destroyAllWindows()  

    print("Morse Code: ", total_morse.replace("¦", " "))
    print("Translated: ", morse_code.from_morse(total_morse))
    return total_morse  
