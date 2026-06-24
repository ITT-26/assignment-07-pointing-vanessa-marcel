# code from google mediapipe's code sample
# adapted to be compatible with opencv live image stream
# https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python

import sys
import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import threading


class HandRecognizerThread:
    def __init__(self, video_id, num_hands, model_path):
        self.num_hands = num_hands

        OPTIONS = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            num_hands=self.num_hands,
            running_mode=vision.RunningMode.VIDEO,
            min_hand_detection_confidence=0.3,
            min_hand_presence_confidence=0.3,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(OPTIONS)
        self.cap = cv2.VideoCapture(video_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, sys.maxsize)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, sys.maxsize)

        self.results = {}

        self.interrupt_event = threading.Event()
        self.lock = threading.Lock()

    def interrupt(self):
        self.interrupt_event.set()

    def run(self):
        while not self.interrupt_event.is_set():
            # Capture a frame from the webcam
            ret, frame = self.cap.read()
            frame = cv2.flip(frame, 1)

            # convert to mediapipe image
            mp_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

            # save current time for internal interpolation
            timestamp_ms = int(time.time() * 1000)

            # Detect hand landmarks from the input image.
            detection_result = self.detector.detect_for_video(
                mp_frame, timestamp_ms)

            hand_landmarks_list = detection_result.hand_landmarks
            if len(hand_landmarks_list) > 0:
                landmarks = hand_landmarks_list[0]

                rel_index_x = landmarks[8].x
                rel_index_y = landmarks[8].y
                print(landmarks[8].z)

                rel_middle_x = landmarks[12].x
                rel_middle_y = landmarks[12].y

                rel_thumb_x = landmarks[4].x
                rel_thumb_y = landmarks[4].y
                
                
                rel_index_start_x = landmarks[5].x
                rel_index_start_y = landmarks[5].y


                index = {"x": rel_index_x, "y": rel_index_y}
                middle_finger = {"x": rel_middle_x, "y": rel_middle_y}
                thumb = {"x": rel_thumb_x, "y": rel_thumb_y}
                index_start = {"x": rel_index_start_x, "y": rel_index_start_y}

                with self.lock:
                    self.results = {
                        "index": index,
                        "middle_finger": middle_finger,
                        "thumb": thumb,
                        "timestamp" : timestamp_ms,
                        "index_start" : index_start
                    }

            else:
                with self.lock:
                    self.results.clear()

                # print(f"middle at {landmarks[12][1]}, {landmarks[12][2]}")
                # print(f"thumb at {landmarks[4][1]}, {landmarks[4][2]}")

                # 8 = Zeigefinger
                # 4 daumen
                # 12 Mittelfinger
            time.sleep(0.001)
        self.stop()

    def stop(self):
        self.cap.release()
