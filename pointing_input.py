# here goes your mediapipe-to-pointer implementation

from hand_recognition.mediapipe_hands import HandRecognizerThread
from pynput.mouse import Controller, Button
import time
import threading
from collections import deque
import copy

VIDEO_ID = 0
NUM_HANDS = 1
MODEL_PATH = './hand_recognition/hand_landmarker.task'

recognizer = HandRecognizerThread(VIDEO_ID, NUM_HANDS, model_path=MODEL_PATH)

run_recognizer_thread = threading.Thread(target=recognizer.run)
run_recognizer_thread.start()

mouse = Controller()

last_index_x = -1
last_index_y = -1

x_velocity_deque = deque(maxlen=10)
y_veloctiy_deque = deque(maxlen=10)


def get_smoothend_finger_positons():
    if len(index_x_deque) == 0:
        return None, None
    index_x = 0
    index_y = 0

    for x, y in zip(index_x_deque, index_y_deque):
        index_x += x
        index_y += y

    index_x /= len(index_x_deque)
    index_y /= len(index_y_deque)

    return index_x, index_y


def get_index_movement():
    global last_index_x, last_index_y

    smooth_x, smooth_y = get_smoothend_finger_positons()
    if smooth_x is None:
        return 0, 0

    dx = smooth_x - last_index_x
    dy = smooth_y - last_index_y
    
    MOVEMENT_THRESH = 0.002
    if abs(dx) < MOVEMENT_THRESH:
        dx = 0
    if abs(dy) < MOVEMENT_THRESH:
        dy = 0

    if last_index_x < 0 or last_index_y < 0:
        dx, dy = 0, 0

    last_index_x = smooth_x
    last_index_y = smooth_y

    return dx, dy

def translate_index_movement_to_mouse_movement(dx, dy):
    SENSITIVITY = 1000
    movement_x *= SENSITIVITY
    movement_y *= SENSITIVITY
    # hier nochmal smooth
    # velocity estiamtion (mit timestamp)
    return movement_x, movement_y

    
def move_mouse(dx, dy):
    mouse.move(dx,dy)

while True:
    with recognizer.lock:
        if recognizer.results:
            print(recognizer.results)
            index_x_deque.append(recognizer.results["index"]["x"])
            # absolute hand positon auf kamera
            index_y_deque.append(recognizer.results["index"]["y"])
        else:
            index_x_deque.clear()
            index_y_deque.clear()
            last_index_x = -1 
            last_index_y = -1

    index_dx, index_dy = get_index_movement()
    mouse_dx, mouse_dy = translate_index_movement_to_mouse_movement(index_dx, index_dy)
    move_mouse(mouse_dx, mouse_dy)
    time.sleep(0.001)

