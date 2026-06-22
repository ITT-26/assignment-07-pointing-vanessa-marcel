# here goes your Steering Law application
import pyglet
import json
from pyglet.window import mouse
from pyglet import window, display, shapes
import sys
import time
from configparser import ConfigParser
import pandas as pd
import random


def setup_window(window):
    maximize_window_size(window)
    window.maximize()
    window.set_caption("Steering Law Application")


def maximize_window_size(window):
    display = pyglet.display.get_display()
    screen = display.get_default_screen()
    window.width = screen.width
    window.height = screen.height


class SteeringApp:
    def __init__(self, window, pid, trials, input_mode):
        self.mouse_state = mouse.MouseStateHandler()
        window.push_handlers(self.mouse_state)
        self.window = window
        self.batch = pyglet.graphics.Batch()
        self.pid = pid
        
        self.trials = trials
        self.current_trial = 1

        self.path_widths, self.distances = self.read_app_params()

        self.combinations = []
        self.current_combination = None

        self.objects = []

        self.mouse_circle = None

        self.trial_start_timestamp = int(time.time())
        self.log_df = self.create_log_df()
        self.DATA_PATH = f"./data/{input_mode}/"

    def read_app_params(self):
        parser = ConfigParser()
        parser.read("config.ini")
        slinfo = parser["SLCONFIG"]
        path_widths = [int(w) for w in slinfo["tunnel_widths"].split(",")]
        distances = [int(d) for d in slinfo["distances"].split(",")]
        return path_widths, distances

    def create_all_combinations(self):
        for width in self.path_widths:
            for distance in self.distances:
                self.combinations.append({
                    "width": width,
                    "distance": distance
                })

    def choose_combination(self):
        index = int(random.random() * len(self.combinations))
        self.current_combination = self.combinations.pop(index)

    def next_combination(self):
        self.save_log_data()
        self.log_df = self.create_log_df()
        self.objects.clear()
        self.choose_combination()
        self.create_path()

    def create_path(self):
        width = self.current_combination["width"]
        distance = self.current_combination["distance"]

        start_x = self.window.width // 2 - distance // 2
        start_y = self.window.height // 2 - width // 2
        start_line = self.draw_start_line(start_x, start_y, length=width)
        self.objects.append(start_line)

        path_rect = self.draw_path_rectangle(start_x, start_y, width, distance)
        self.objects.append(path_rect)

        goal_x = start_x + distance
        goal_y = start_y
        goal_line = self.draw_goal_line(goal_x, goal_y, length=width)
        self.objects.append(goal_line)

    def draw_path_rectangle(self, x, y, width, distance):
        path_rect = shapes.Rectangle(
            x, y, distance, width, color=(255, 130, 130), batch=self.batch)
        return path_rect

    def draw_start_line(self, x, y, length):
        start_line = shapes.Line(
            x, y, x, y+length, thickness=15, color=(26, 128, 0), batch=self.batch
        )
        return start_line

    def draw_goal_line(self, x, y, length):
        goal_line = shapes.Line(
            x, y, x, y+length, thickness=15, color=(26, 128, 0), batch=self.batch
        )
        return goal_line

    def draw_mouse_circle(self):
        RADIUS = 5
        center_offset = RADIUS//2
        mouse_circle = shapes.Circle(
            self.mouse_state["x"] - center_offset, self.mouse_state["y"] - center_offset, radius=RADIUS, color=(0, 255, 0), batch=self.batch)
        self.mouse_circle = mouse_circle

    def update_mouse_circle(self, target_x, target_y):
        center_offset = self.mouse_circle.radius // 2
        self.mouse_circle.x = target_x - center_offset
        self.mouse_circle.y = target_y - center_offset

    def set_start_timestamp(self):
        self.trial_start_timestamp = int(time.time())

    def create_log_df(self):
        df = pd.DataFrame(columns=["iteration", "pid", "path_w",
                          "path_d", "success", "start_timestamp", "end_timestamp"])
        return df

    def add_data_line(self, success: bool):
        line = {
            "iteration": self.current_trial,
            "pid": self.pid,
            "path_w": self.path_width,
            "path_d": self.distance,
            "success": success,
            "start_timestamp": self.trial_start_timestamp,
            "end_timestamp": int(time.time())
        }
        self.log_df.loc[len(self.log_df)] = line

    def save_log_data(self):
        self.log_df.to_csv(
            f"{self.DATA_PATH}steering_{self.path_width}_{self.distance}_{self.pid}", index=False)

    def next_trial(self):
        self.current_trial += 1
        self.objects.clear()
        self.create_path()

    def end_app(self):
        self.save_log_data()
        pyglet.app.exit()

    def cross_start_line(self):
        self.set_start_timestamp()

    def cross_goal_line(self):
        self.add_data_line(success=True)
        if self.current_trial < self.trials:
            self.next_trial()
        else:
            self.current_trial = 1
            self.next_combination()

    def unsuccessful_try(self):
        self.add_data_line(success=False)
        if self.current_trial < self.trials:
            self.next_trial()
        else:
            self.current_trial = 1
            self.next_combination()


win = window.Window(vsync=False)

setup_window(win)

participantID = 0
trials = 1
input_mode = "unknown" 

# first command line input is participant-ID
if len(sys.argv) > 1:
    participantID = int(sys.argv[1])

# second command line input is trial-amount
if len(sys.argv) > 2:
    trials = int(sys.argv[2])

# third command line input is input mode (relevant for logging)
if len(sys.argv) > 3:
    input_mode = int(sys.argv[3])


app = SteeringApp(win, participantID, trials, input_mode)
app.start()


@win.event
def on_mouse_enter(x, y):
    app.draw_mouse_circle()


@win.event
def on_mouse_motion(x, y, dx, dy):
    app.update_mouse_circle(x, y)


@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    app.update_mouse_circle(x, y)


@win.event
def on_mouse_press(x, y, button, modifiers):
    pass


@win.event
def on_draw():
    win.clear()
    app.batch.draw()


pyglet.app.run()
