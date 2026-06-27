# here goes your Fitts' Law application
import pyglet
from pyglet import window, shapes
from pyglet.window import mouse
import sys
from configparser import ConfigParser
import math
import time
import os
import csv
import random
from pathlib import Path
from collections import deque

participantID = 0
trials = 3

config_object = ConfigParser()

config_object.read("config.ini")

flinfo = config_object["FLCONFIG"]

target_widths = [int(w) for w in flinfo["target_widths"].split(",")]
target_distances = [int(d) for d in flinfo["target_distances"].split(",")]
target_w = 0
target_d = 0
target_r = 0
target_amount = int(flinfo["target_amount"])

current_target = 0
counter = 0
trial_count = 1
input = 0
data = [["iteration", "pid", "num_targets", "target_w",
         "target_d", "target_id", "timestamp", "input"]]
inputs = ["pose", "mouse", "latency", "touchpad"]
combinations = []
combi_count = 1
combi_amount = 0

PADDING = 50

circles = []
mouse_circle = None

batch = pyglet.graphics.Batch()

motion_events = deque()
click_events = deque()

# first command line input is participant-ID
if len(sys.argv) > 1:
    participantID = int(sys.argv[1])

# second command line input is trial-amount
if len(sys.argv) > 2:
    trials = int(sys.argv[2])

# third command for input method
if len(sys.argv) > 3:
    input = int(sys.argv[3])


class Circle:
    def __init__(self, x, y):
        self.circle = shapes.Circle(
            x, y, target_r, color=(128, 128, 128), batch=batch)

    def setColour(self, on):
        if on:
            self.circle.color = (255, 0, 0)
        else:
            self.circle.color = (128, 128, 128)

    def delete(self):
        self.circle.delete()


def addData():
    global trial_count, participantID, target_amount, target_w, target_d, counter, inputs, input
    data.append([trial_count, participantID, target_amount, target_w,
                target_d, counter, int(time.time()), inputs[input]])
    # print(data[-1])


def updateFl():
    global current_target
    circles[int(current_target)].setColour(False)
    if current_target < target_amount/2:
        current_target = current_target + target_amount/2
    else:
        current_target = current_target - target_amount/2 + 1
    circles[int(current_target)].setColour(True)


def saveData():
    path = Path(f"./data/{inputs[input]}/")
    path.mkdir(parents=True, exist_ok=True)
    filename = f"{path}/fitts_{target_amount}_{target_w}_{target_d}_{participantID}.csv"
    with open(filename, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(data)


def createAllCombinations():
    global combi_amount
    for width in target_widths:
        for distance in target_distances:
            combinations.append({
                "width": width,
                "distance": distance
            })
    combi_amount = len(combinations)


def chooseCombination():
    global target_w, target_r, target_d
    index = random.randrange(0, len(combinations))
    target_w = combinations[index]["width"]
    target_r = target_w/2
    target_d = combinations[index]["distance"]
    combinations.pop(index)


createAllCombinations()
chooseCombination()


def setup_window(window):
    maximize_window_size(window)
    window.maximize()
    window.set_caption("Steering Law Application")


def maximize_window_size(window):
    display = pyglet.display.get_display()
    screen = display.get_default_screen()
    window.width = screen.width
    window.height = screen.height


win = window.Window()
setup_window(win)


def setupFL():
    global target_amount, target_d, current_target, data, counter
    circles[0].setColour(True)
    current_target = 0
    counter = 0


def createCircles():
    global target_d, target_amount
    center_x = win.width//2
    center_y = win.height//2
    rad = target_d/2
    for i in range(target_amount):
        angle = -(2 * math.pi * i / target_amount)
        x = center_x + (rad * math.sin(angle))
        y = center_y + (rad * math.cos(angle))

        circles.append(Circle(x, y))


def resetCircles():
    for c in circles:
        c.delete()
    circles.clear()
    createCircles()


createCircles()
setupFL()


def create_mouse_circle(x, y):
    global mouse_circle

    RADIUS = 5
    center_offset = RADIUS//2
    mouse_circle = shapes.Circle(
        x - center_offset, y - center_offset, radius=RADIUS, color=(0, 255, 0), batch=batch)


def update_mouse_circle(target_x, target_y):
    global mouse_circle

    center_offset = mouse_circle.radius // 2
    mouse_circle.x = target_x - center_offset
    mouse_circle.y = target_y - center_offset


@win.event
def on_mouse_press(x, y, button, modifiers):
    global input
    t = time.time()

    if inputs[input] == "latency":
        t = time.time() + 0.150 

    click_events.append({
        "t": t,
        "x": x,
        "y": y,
    })


def perform_click_event(x, y):
    global target_w, target_r, current_target, target_amount, counter, trial_count, trials, combi_count, combi_amount
    if x > circles[int(current_target)].circle.x - target_r and x < circles[int(current_target)].circle.x + target_r and y > circles[int(current_target)].circle.y - target_r and y < circles[int(current_target)].circle.y + target_r:
        if counter == target_amount-1:
            addData()
            counter += 1
            circles[int(current_target)].setColour(False)
            trial_count += 1
            if trial_count >= trials:
                saveData()
                # print(combi_count)
                if combi_count == combi_amount:
                    os._exit(0)
                chooseCombination()
                resetCircles()
                combi_count += 1
                trial_count = 0
            setupFL()
        else:
            addData()
            counter += 1
            updateFl()


@win.event
def on_mouse_enter(x, y):
    create_mouse_circle(x, y)


@win.event
def on_mouse_motion(x, y, dx, dy):
    global input
    t = time.time()

    if inputs[input] == "latency":
        t = time.time() + 0.150 

    motion_events.append({
        "t": t,
        "x": x,
        "y": y,
        "dx": dx
    })
    


def perform_motion_event(x, y):
    global mouse_circle
    if mouse_circle is not None:
        update_mouse_circle(x, y)
        
def mouse_events_polling(dt):
    t = time.time()
    while motion_events and t >= motion_events[0]["t"]:
        m_event = motion_events.popleft()
        perform_motion_event(m_event["x"], m_event["y"])
        
    t = time.time()
    while click_events and t >= click_events[0]["t"]:
        c_event = click_events.popleft()
        perform_click_event(c_event["x"], c_event["y"])
        
@win.event
def on_draw():
    win.clear()
    batch.draw()

pyglet.clock.schedule_interval(mouse_events_polling, 0.005)
pyglet.app.run()
