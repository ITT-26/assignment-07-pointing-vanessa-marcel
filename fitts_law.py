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

participantID = 0
trials = 5

config_object = ConfigParser()

config_object.read("config.ini")

flinfo = config_object["FLCONFIG"]

target_w = int(flinfo["target_w"])
target_d = int(flinfo["target_d"])
target_r = target_w /2
target_amount = int(flinfo["target_amount"])

current_target = 0
counter = 0
trial_count = 1
data = [["iteration", "pid", "num_targets", "target_w", "target_d", "target_id", "timestamp"]]

PADDING = 50
WINDOW_SIZE = (2*PADDING + 2*target_w + target_d)

win = window.Window(WINDOW_SIZE, WINDOW_SIZE)

circles = []
batch = pyglet.graphics.Batch()

# first command line input is participant-ID
if len(sys.argv) > 1:
    participantID = int(sys.argv[1])

# second command line input is trial-amount
if len(sys.argv) > 2:
    trials = int(sys.argv[2])

class Circle:
    def __init__(self, x, y):
        self.circle = shapes.Circle(x, y, target_r, color=(128, 128, 128), batch=batch)
    
    def setColour(self, on):
        if on:
            self.circle.color = (255, 0, 0)
        else:
            self.circle.color = (128, 128, 128)

def addData():
    global trial_count, participantID, target_amount, target_w, target_d, counter
    data.append([trial_count, participantID, target_amount, target_w, target_d, counter, int(time.time())])
    print(data[-1])

def updateFl():
    global current_target
    circles[int(current_target)].setColour(False)
    if current_target < target_amount/2:
        current_target = current_target + target_amount/2
    else:
        current_target = current_target - target_amount/2 + 1
    circles[int(current_target)].setColour(True)

def saveData():
    filename = f"data/fitts_{target_amount}_{target_d}_{target_w}_{participantID}.csv"
    with open(filename, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(data)


def setupFL():
    global target_amount, target_d, current_target, data, counter
    circles[0].setColour(True)
    current_target = 0
    counter = 0

def createCircles():
    global target_d, target_amount
    center = WINDOW_SIZE/2
    rad = target_d/2
    for i in range(target_amount):
        angle = -(2 * math.pi * i / target_amount)
        x = center + (rad * math.sin(angle))
        y = center + (rad * math.cos(angle))

        circles.append(Circle(x, y))

createCircles()
setupFL()

@win.event
def on_mouse_press(x, y, button, modifiers):
    global target_w, target_r, current_target, target_amount, counter, trial_count, trials
    if x > circles[int(current_target)].circle.x - target_r and x < circles[int(current_target)].circle.x + target_r and y > circles[int(current_target)].circle.y - target_r and y < circles[int(current_target)].circle.y + target_r:
        if counter == target_amount-1:
            addData()
            counter += 1
            circles[int(current_target)].setColour(False)
            if trial_count == trials:
                saveData()    
                os._exit(0)
            setupFL()
            print(trial_count)
            trial_count += 1
            print(trial_count)
        else:
            addData()
            counter += 1
            updateFl()     

@win.event
def on_draw():
    win.clear()
    batch.draw()

pyglet.app.run()
