# import cv2
# import mediapipe as mp
# import numpy as np
# import time
# from collections import deque

# mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp_face_mesh.FaceMesh(
#     static_image_mode=False,
#     max_num_faces=1,
#     refine_landmarks=True,
#     min_detection_confidence=0.5,
#     min_tracking_confidence=0.5)

# drawing_utils = mp.solutions.drawing_utils
# LIPS = mp_face_mesh.FACEMESH_LIPS
# LEFT_IRIS = [468, 469, 470, 471]
# RIGHT_IRIS = [473, 474, 475, 476]

# recent_emotions = deque(maxlen=5)

# def distance(p1, p2):
#     return np.linalg.norm(np.array([p1.x, p1.y]) - np.array([p2.x, p2.y]))

# def get_emotion(landmarks):
#     top_lip = landmarks[13]
#     bottom_lip = landmarks[14]
#     left_mouth = landmarks[61]
#     right_mouth = landmarks[291]
#     left_eye_top = landmarks[159]
#     left_eye_bottom = landmarks[145]
#     right_eye_top = landmarks[386]
#     right_eye_bottom = landmarks[374]
#     left_brow = landmarks[70]
#     right_brow = landmarks[300]
#     iris_left = landmarks[468]
#     iris_right = landmarks[473]
#     face_width = distance(landmarks[234], landmarks[454])

#     mouth_open = distance(top_lip, bottom_lip) / face_width
#     mouth_width = distance(left_mouth, right_mouth) / face_width
#     mouth_corner_drop = ((left_mouth.y + right_mouth.y) / 2) - ((top_lip.y + bottom_lip.y) / 2)
#     eye_open_left = distance(left_eye_top, left_eye_bottom) / face_width
#     eye_open_right = distance(right_eye_top, right_eye_bottom) / face_width
#     eye_open_avg = (eye_open_left + eye_open_right) / 2
#     brow_eye_dist = ((left_brow.y - left_eye_top.y) + (right_brow.y - right_eye_top.y)) / 2
#     eye_top_avg = (left_eye_top.y + right_eye_top.y) / 2
#     eye_bottom_avg = (left_eye_bottom.y + right_eye_bottom.y) / 2
#     iris_avg = (iris_left.y + iris_right.y) / 2
#     eye_center_y = (eye_top_avg + eye_bottom_avg) / 2
#     sad_offset = iris_avg - eye_center_y

#     if mouth_width > 0.42 and mouth_open < 0.06:
#         return "happy"
#     elif mouth_open >= 0.14 and eye_open_avg > 0.085:
#         return "surprise"
#     elif mouth_open > 0.06 and eye_open_avg > 0.07 and sad_offset < -0.005:
#         return "fear"
#     elif (mouth_corner_drop > 0.015 and brow_eye_dist < 0.045) or (sad_offset > 0.006 and eye_open_avg < 0.05):
#         return "sad"
#     elif mouth_open < 0.03 and eye_open_avg < 0.07 and mouth_width < 0.38:
#         return "disgust"
#     elif eye_open_avg > 0.095 and mouth_open < 0.05:
#         return "angry"
#     else:
#         return "neutral"

# cap = cv2.VideoCapture(0)
# prev_time = 0

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to grab frame")
#         break

#     frame = cv2.flip(frame, 1)
#     h, w, _ = frame.shape
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(rgb)

#     emotion = "neutral"

#     if results.multi_face_landmarks:
#         for face_landmarks in results.multi_face_landmarks:
#             emotion = get_emotion(face_landmarks.landmark)
#             recent_emotions.append(emotion)
#             emotion = max(set(recent_emotions), key=recent_emotions.count)
#             print(f"Emotion detected: {emotion}, Landmarks: {len(face_landmarks.landmark)}")

#             # Draw simple face mesh
#             drawing_utils.draw_landmarks(
#                 frame,
#                 face_landmarks,
#                 mp_face_mesh.FACEMESH_TESSELATION,
#                 drawing_utils.DrawingSpec(color=(0,255,0), thickness=1, circle_radius=1),
#                 drawing_utils.DrawingSpec(color=(0,0,255), thickness=1))

#     curr_time = time.time()
#     fps = 1 / (curr_time - prev_time) if prev_time else 0
#     prev_time = curr_time

#     cv2.putText(frame, f"Emotion: {emotion}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
#     cv2.putText(frame, f"FPS: {int(fps)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

#     cv2.imshow("Raspberry Pi Face Mesh & Emotion", frame)

#     if cv2.waitKey(1) & 0xFF == 27:  # ESC key to quit
#         break

# cap.release()
# cv2.destroyAllWindows()



import cv2
import dlib
import numpy as np
import time
from collections import deque

# Load dlib's face detector & shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

recent_emotions = deque(maxlen=5)

def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def get_emotion(landmarks):
    # Convert dlib shape to NumPy array
    points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)], dtype=np.float32)

    # Map roughly equivalent MediaPipe points to dlib's 68 points
    top_lip = points[62]
    bottom_lip = points[66]
    left_mouth = points[48]
    right_mouth = points[54]
    left_eye_top = points[37]
    left_eye_bottom = points[41]
    right_eye_top = points[43]
    right_eye_bottom = points[47]
    left_brow = points[21]
    right_brow = points[22]
    iris_left = points[39]  # Approximation (inner eye corner)
    iris_right = points[42] # Approximation (inner eye corner)
    face_width = distance(points[0], points[16])

    mouth_open = distance(top_lip, bottom_lip) / face_width
    mouth_width = distance(left_mouth, right_mouth) / face_width
    mouth_corner_drop = ((left_mouth[1] + right_mouth[1]) / 2) - ((top_lip[1] + bottom_lip[1]) / 2)
    eye_open_left = distance(left_eye_top, left_eye_bottom) / face_width
    eye_open_right = distance(right_eye_top, right_eye_bottom) / face_width
    eye_open_avg = (eye_open_left + eye_open_right) / 2
    brow_eye_dist = ((left_brow[1] - left_eye_top[1]) + (right_brow[1] - right_eye_top[1])) / 2
    eye_top_avg = (left_eye_top[1] + right_eye_top[1]) / 2
    eye_bottom_avg = (left_eye_bottom[1] + right_eye_bottom[1]) / 2
    iris_avg = (iris_left[1] + iris_right[1]) / 2
    eye_center_y = (eye_top_avg + eye_bottom_avg) / 2
    sad_offset = iris_avg - eye_center_y

    # Same rules as your original
    if mouth_width > 0.42 and mouth_open < 0.06:
        return "happy"
    elif mouth_open >= 0.14 and eye_open_avg > 0.085:
        return "surprise"
    elif mouth_open > 0.06 and eye_open_avg > 0.07 and sad_offset < -0.005:
        return "fear"
    elif (mouth_corner_drop > 0.015 and brow_eye_dist < 0.045) or (sad_offset > 0.006 and eye_open_avg < 0.05):
        return "sad"
    elif mouth_open < 0.03 and eye_open_avg < 0.07 and mouth_width < 0.38:
        return "disgust"
    elif eye_open_avg > 0.095 and mouth_open < 0.05:
        return "angry"
    else:
        return "neutral"

cap = cv2.VideoCapture(0)
prev_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    emotion = "neutral"

    for face in faces:
        landmarks = predictor(gray, face)
        emotion = get_emotion(landmarks)
        recent_emotions.append(emotion)
        emotion = max(set(recent_emotions), key=recent_emotions.count)

        # Draw landmarks
        for n in range(68):
            x, y = landmarks.part(n).x, landmarks.part(n).y
            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time else 0
    prev_time = curr_time

    cv2.putText(frame, f"Emotion: {emotion}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("Raspberry Pi Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
