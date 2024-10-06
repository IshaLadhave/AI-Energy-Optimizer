import cv2
import mediapipe as mp
import numpy as np
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize pycaw for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get volume range
vol_min, vol_max = volume.GetVolumeRange()[:2]

# Initialize camera
cap = cv2.VideoCapture(0)

def get_landmark_coords(landmarks, index, frame_shape):
    """Convert landmark index to pixel coordinates."""
    return np.array([int(landmarks.landmark[index].x * frame_shape[1]),
                     int(landmarks.landmark[index].y * frame_shape[0])])

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Flip image for selfie-view
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = mp_hands.process(img_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw hand landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

                # Get coordinates for thumb tip and index finger tip
                thumb_tip = get_landmark_coords(hand_landmarks, mp.solutions.hands.HandLandmark.THUMB_TIP, frame.shape)
                index_tip = get_landmark_coords(hand_landmarks, mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP, frame.shape)

                # Draw circles at the thumb and index finger tips
                cv2.circle(frame, tuple(thumb_tip), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(frame, tuple(index_tip), 10, (255, 0, 0), cv2.FILLED)

                # Calculate distance between thumb and index finger
                distance = np.linalg.norm(thumb_tip - index_tip)

                # Map distance to volume control
                volume_level = np.interp(distance, [30, 300], [vol_min, vol_max])
                volume.SetMasterVolumeLevel(volume_level, None)

        # Show the frame
        cv2.imshow('Volume Control', frame)

        # Break loop on 'q' key press
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
