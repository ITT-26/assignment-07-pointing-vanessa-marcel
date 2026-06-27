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
from pathlib import Path
from collections import deque


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
        self.foreground_group = pyglet.graphics.Group(1)
        self.pid = pid

        self.trials = trials
        self.current_trial = 1

        self.path_widths, self.distances = self.read_app_params()

        self.combinations = []
        self.current_combination = None

        self.points = []
        self.lines = []

        self.mouse_circle = None

        self.trial_start_timestamp = int(time.time())
        self.log_df = self.create_log_df()

        self.DATA_PATH = Path(f"./data/{input_mode}/")
        self.DATA_PATH.mkdir(parents=True, exist_ok=True)
        self.input_mode = input_mode

        self.start_line = None
        self.goal_line = None
        self.path_rect = None

        self.run_started = False

        self.motion_events = deque()

    def start(self):
        self.create_all_combinations()
        self.choose_combination()
        self.create_log_df()
        self.create_path()

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
        self.current_trial = 1
        self.save_log_data()
        self.log_df = self.create_log_df()
        self.choose_combination()
        self.create_path()

    def create_path(self):
        width = self.current_combination["width"]
        distance = self.current_combination["distance"]

        start_x = self.window.width // 2 - distance // 2
        start_y = self.window.height // 2 - width // 2

        self.path_rect = self.draw_path_rectangle(
            start_x, start_y, width, distance)

        self.start_line = self.draw_start_line(start_x, start_y, length=width)

        goal_x = start_x + distance
        goal_y = start_y

        self.goal_line = self.draw_goal_line(goal_x, goal_y, length=width)

    def draw_path_rectangle(self, x, y, width, distance):
        path_rect = shapes.Rectangle(
            x, y, distance, width, color=(255, 130, 130), batch=self.batch)
        return path_rect

    def draw_start_line(self, x, y, length):
        start_line = shapes.Line(
            x, y, x, y+length, thickness=5, color=(26, 128, 0), batch=self.batch
        )
        return start_line

    def draw_goal_line(self, x, y, length):
        goal_line = shapes.Line(
            x, y, x, y+length, thickness=5, color=(26, 128, 0), batch=self.batch
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
                          "path_d", "success", "start_timestamp", "end_timestamp", "input_mode"])
        return df

    def add_data_line(self, success: bool):
        line = {
            "iteration": self.current_trial,
            "pid": self.pid,
            "path_w": self.current_combination["width"],
            "path_d": self.current_combination["distance"],
            "success": success,
            "start_timestamp": self.trial_start_timestamp,
            "end_timestamp": int(time.time()),
            "input_mode": self.input_mode
        }

        self.log_df.loc[len(self.log_df)] = line

    def save_log_data(self):
        file = f"{self.DATA_PATH}/steering_{self.current_combination["width"]}_{self.current_combination["distance"]}_{self.pid}.csv"
        self.log_df.to_csv(
            file, index=False)

    def next_trial(self):
        self.current_trial += 1
        self.create_path()

    def end_app(self):
        self.save_log_data()
        self.window.close()
        pyglet.app.exit()

    def cross_start_line(self):
        self.points.clear()
        self.lines.clear()
        self.set_start_timestamp()
        self.run_started = True

    def cross_goal_line(self):
        self.lines.clear()
        self.points.clear()
        self.add_data_line(success=True)
        self.run_started = False
        if self.current_trial < self.trials:
            self.next_trial()
        elif len(self.combinations) > 0:
            self.next_combination()
        else:
            self.end_app()

    def complete_unsuccessful_try(self):
        self.lines.clear()
        self.points.clear()
        self.add_data_line(success=False)
        self.run_started = False
        if self.current_trial < self.trials:
            self.next_trial()
        elif len(self.combinations) > 0:
            self.next_combination()
        else:
            self.end_app()

    def add_line_point(self, x, y):
        self.points.append((x, y))

        if len(self.points) >= 2:
            last_x, last_y = self.points[-2]

            self.lines.append(shapes.Line(
                last_x, last_y, x, y,
                thickness=5,
                color=(0, 200, 0),
                batch=self.batch, group=self.foreground_group)
            )


win = window.Window(vsync=False)

setup_window(win)

participantID = 0
trials = 1


input = 0
inputs = ["pose", "mouse", "latency", "touchpad"]

# first command line input is participant-ID
if len(sys.argv) > 1:
    participantID = int(sys.argv[1])

# second command line input is trial-amount
if len(sys.argv) > 2:
    trials = int(sys.argv[2])

# third command line input is input mode (relevant for logging)
if len(sys.argv) > 3:
    input = int(sys.argv[3])

input_mode = inputs[input]

app = SteeringApp(win, participantID, trials, input_mode)
app.start()


@win.event
def on_mouse_enter(x, y):
    app.draw_mouse_circle()


@win.event
def on_mouse_motion(x, y, dx, dy):
    t = time.time()

    if app.input_mode == "latency":
        t = time.time() + 0.150

    app.motion_events.append({
        "t": t,
        "x": x,
        "y": y,
        "dx": dx
    })


@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    t = time.time()

    if app.input_mode == "latency":
        t = time.time() + 0.150

    app.motion_events.append({
        "t": t,
        "x": x,
        "y": y,
        "dx": dx
    })


def perform_mouse_motion_event(x, y, dx):
    app.update_mouse_circle(x, y)
    path_top = app.path_rect.y + app.path_rect.height
    old_x = x - dx
    if y > app.path_rect.y and y < path_top:
        if app.run_started:
            app.add_line_point(x, y)
        if x >= app.start_line.x and old_x <= app.start_line.x and not app.run_started:  # and
            app.cross_start_line()
            return
        if app.run_started and x >= app.goal_line.x and old_x <= app.goal_line.x:
            app.cross_goal_line()
            return
    if app.run_started:
        if y > path_top or y < app.path_rect.y:
            app.complete_unsuccessful_try()


def motion_events_polling(dt):
    t = time.time()
    while app.motion_events and t >= app.motion_events[0]["t"]:
        m_event = app.motion_events.popleft()
        perform_mouse_motion_event(m_event["x"], m_event["y"], m_event["dx"])


@win.event
def on_draw():
    win.clear()
    app.batch.draw()


pyglet.clock.schedule_interval(motion_events_polling, 0.005)
pyglet.app.run()
