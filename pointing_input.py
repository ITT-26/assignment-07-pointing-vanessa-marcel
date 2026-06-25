# here goes your mediapipe-to-pointer implementation

from hand_recognition.mediapipe_hands import HandRecognizerThread
from pynput.mouse import Controller, Button
import time
import threading
from collections import deque
import sys
from pynput import keyboard

VIDEO_ID = 0
NUM_HANDS = 1
MODEL_PATH = './hand_recognition/hand_landmarker.task'

recognizer = HandRecognizerThread(VIDEO_ID, NUM_HANDS, model_path=MODEL_PATH)

recognizer_thread = threading.Thread(target=recognizer.run)
recognizer_thread.start()

mouse = Controller()

last_index_x = None
last_index_y = None
last_timestamp = int(time.time() * 1000)
last_recog_time = time.time()

DEQUE_LEN = 10

x_speed_deque = deque(maxlen=DEQUE_LEN)
y_speed_deque = deque(maxlen=DEQUE_LEN)

CLICK_THRESHOLD = 0.04
last_click = 0


is_running = True

sensitivity = 50

if len(sys.argv) > 1:
    sensitivity = int(sys.argv[1])


def get_velocity_avgs():
    if len(x_speed_deque) == 0 or len(y_speed_deque) == 0:
        return 0, 0
    speed_x = 0
    speed_y = 0

    for x, y in zip(x_speed_deque, y_speed_deque):
        speed_x += x
        speed_y += y

    speed_x /= len(x_speed_deque)
    speed_y /= len(y_speed_deque)

    return speed_x, speed_y


def get_index_deltas(x, y):
    global last_index_x, last_index_y

    if last_index_x is None:
        last_index_x = x
        last_index_y = y
        return 0, 0

    dx = x - last_index_x
    dy = y - last_index_y

    last_index_x = x
    last_index_y = y

    return dx, dy


def translate_speed_to_mouse_movement(speed_x, speed_y):
    global sensitivity

    movement_x = sensitivity * speed_x 
    movement_y = sensitivity * speed_y 

    return movement_x, movement_y


def move_mouse(dx, dy):
    mouse.move(int(dx), int(dy))


def checkForClick(thumb_x, thumb_y, mid_x, mid_y):
    global last_click
    if (mid_x - thumb_x) > -CLICK_THRESHOLD and (mid_x - thumb_x) < CLICK_THRESHOLD and (mid_y - thumb_y) > -CLICK_THRESHOLD and (mid_y - thumb_y):
        if (time.time() - last_click) >= 0.5:
            # print("click")
            mouse.press(Button.left)
            mouse.release(Button.left)
            last_click = time.time()
            # print(last_click)
    else:
        pass


def on_key_press(key):
    global is_running
    try:
        if key.char == 'q':
            recognizer.interrupt()
            recognizer_thread.join()
            is_running = False
            return False  # stop listener
    except AttributeError:
        if key == keyboard.Key.esc:
            recognizer.interrupt()
            recognizer_thread.join()
            is_running = False
            return False  # stop listener


listener = keyboard.Listener(on_press=on_key_press).start()


while is_running:
    mouse_dx = 0
    mouse_dy = 0
    
    index_x  = None
    index_y = None  
    index_start_x = None
    index_start_y = None
    middle_x = None
    middle_y = None
    thumb_x = None
    thumb_y = None
    timestamp = None
    
    with recognizer.lock:
        time_without_recog = 0
        if recognizer.results:
            # print(recognizer.results)
            index_x = recognizer.results["index"]["x"]
            # absolute hand positon auf kamera
            index_y = recognizer.results["index"]["y"]

            index_start_x = recognizer.results["index_start"]["x"]
            index_start_y = recognizer.results["index_start"]["y"]

            middle_x = recognizer.results["middle_finger"]["x"]
            middle_y = recognizer.results["middle_finger"]["y"]
            thumb_x = recognizer.results["thumb"]["x"]
            thumb_y = recognizer.results["thumb"]["y"]
            timestamp = recognizer.results["timestamp"]
        else:
            last_timestamp = int(time.time() * 1000.0)

            time_without_recog = time.time() - last_recog_time

        if time_without_recog >= 1:
            last_index_x = None
            last_index_y = None

            x_speed_deque.clear()
            y_speed_deque.clear()

        else:
            if len(x_speed_deque) > 0 and len(y_speed_deque) > 0:
                x_speed_deque.append(x_speed_deque[-1])
                y_speed_deque.append(y_speed_deque[-1])
                
    if None not in [middle_x, middle_y, thumb_x, thumb_y]: 
        if index_y < index_start_y:      
            checkForClick(thumb_x, thumb_y, middle_x, middle_y)
    
    if None not in [index_x, index_y, index_start_y, timestamp]:
        if index_y < index_start_y:
            # maus bewgung nur wenn finger spitze über dem gelenk ist

           
            dt = (timestamp - last_timestamp)
            last_timestamp = timestamp
            last_recog_time = timestamp / 1000
            if dt > 0:
                index_dx, index_dy = get_index_deltas(index_x, index_y)

                dt_s = dt / 1000
                speed_x = index_dx / dt_s
                speed_y = index_dy / dt_s

                SPEED_THRESH = 0.03
                if abs(speed_x) < SPEED_THRESH:
                    speed_x = 0
                if abs(speed_y) < SPEED_THRESH:
                    speed_y = 0
                    
                x_speed_deque.append(speed_x)
                y_speed_deque.append(speed_y)

                speed_x, speed_y = get_velocity_avgs()
               

                mouse_dx, mouse_dy = translate_speed_to_mouse_movement(
                    speed_x, speed_y)

                move_mouse(mouse_dx, mouse_dy)
                
    time.sleep(0.01)
