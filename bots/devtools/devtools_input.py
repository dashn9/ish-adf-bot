import random
import time
from threading import Thread

import pyautogui
import pytweening
from selenium.webdriver.remote import webdriver as remote_webdriver
from constants.keyboard_keys import Keys
from pyclick import HumanCurve

from bots import utils


class Keyboard:
    def __init__(self, webdriver: remote_webdriver.WebDriver):
        self.webdriver = webdriver
        self.modifiers = 0
        self.is_key_down = False
        self.down_key_number_of_consecutive_runs = 0
        self.pressed_keys = set()

    def down(self, key, options={"text": "", "keypad": False}, simple=False):
        description = self.key_description_for_string(key)

        pressed_keys = self.pressed_keys
        auto_repeat = False
        if description["code"] in pressed_keys:
            auto_repeat = True

        pressed_keys.add(description["code"])
        is_keypad = True
        type = "keyDown"
        text = ""
        if not simple:
            self.modifiers |= self.modifier_bit(description["key"])
            text = (
                str(options["text"])
                if "text" in options and text != ""
                else description["text"]
            )
            type = "keyDown" if text else "rawKeyDown"
            if "location" in description and description["location"] != 3:
                is_keypad = False
        self.webdriver.execute_cdp_cmd(
            "Input.dispatchKeyEvent",
            dict(
                type=type,
                modifiers=self.modifiers,
                windowsVirtualKeyCode=description["key_code"],
                code=description["code"],
                key=description["key"],
                text=text,
                unmodifiedText=text,
                autoRepeat=auto_repeat,
                location=description["location"],
                isKeypad=is_keypad,
            ),
        )

    def down_persistent(self, key, options={"text": ""}):
        def inner_loop():
            try:
                self.down(key, options, True)
                time.sleep(random.uniform(0.5, 0.52))
                while self.is_key_down:
                    self.down(key, options, True)
                    time.sleep(random.uniform(0.04, 0.07))
                    # self.down_key_number_of_consecutive_runs += 1
                self.down_key_number_of_consecutive_runs = 0
            except Exception:
                pass

        if not self.is_key_down:
            self.is_key_down = True
            return Thread(target=inner_loop).start()

    def modifier_bit(self, key):
        if key == "Alt":
            return 1
        if key == "Control":
            return 2
        if key == "Meta":
            return 4
        if key == "Shift":
            return 8
        return 0

    def key_description_for_string(self, key):
        shift = self.modifiers & 8
        description = dict(key="", keyCode=0, code="", text="", location=0)

        if "key" in key:
            description["key"] = key["key"]
        if shift and key["shift_key"] in key:
            description["key"] = key["shift_key"]

        if "key_code" in key:
            description["key_code"] = key["key_code"]
        if shift and key["shift_key_code"] in key:
            description["key_code"] = key["shift_key_code"]

        if "code" in key:
            description["code"] = key["code"]

        if "location" in key:
            description["location"] = key["location"]

        if len(description["key"]) == 1:
            description["text"] = description["key"]

        if "text" in key:
            description["text"] = key["text"]
        if shift and "shiftText" in key:
            description["text"] = key["shiftText"]

        # if any modifiers besides shift are pressed, no text should be sent
        if self.modifiers & ~8:
            description["text"] = ""

        return description

    def up(self, key):
        description = self.key_description_for_string(key)
        self.modifiers &= ~self.modifier_bit(description["key"])
        if self.is_key_down:
            self.is_key_down = False
            self.pressed_keys.discard(description["code"])

            while self.down_key_number_of_consecutive_runs != 0:
                time.sleep(0.1)

            self.webdriver.execute_cdp_cmd(
                "Input.dispatchKeyEvent",
                dict(
                    type="keyUp",
                    modifiers=self.modifiers,
                    key=description["key"],
                    windowsVirtualKeyCode=description["key_code"],
                    code=description["code"],
                    location=description["location"],
                ),
            )

    def send_character(self, char: str):
        self.webdriver.execute_cdp_cmd("Input.insertText", {"text": char})

    def type(self, text: str, options={"delay": 0}):
        delay = 0
        if options and options.delay:
            delay = options.delay
        for char in text:
            if Keys[char]:
                self.press(char, {delay})
            else:
                self.send_character(char)
            if delay:
                time.sleep(delay)

    def press(self, key, options=(0,)):
        delay = options
        self.down(key, options)
        if delay:
            time.sleep(delay)
        self.up(key)


class Mouse:
    def __init__(self, webdriver: remote_webdriver.WebDriver, keyboard: Keyboard):
        self.webdriver = webdriver
        self.keyboard = keyboard
        self.x = 0
        self.y = 0

    def move(self, x, y, options={"steps": 10}):
        steps = options["steps"]
        from_x = self.x
        from_y = self.y
        self.x = x
        self.y = y
        for i in range(steps):
            self.webdriver.execute_cdp_cmd(
                "Input.dispatchMouseEvent",
                dict(
                    type="mouseMoved",
                    x=from_x + (self.x - from_x) * (i / steps),
                    y=from_y + (self.y - from_y) * (i / steps),
                    modifiers=self.keyboard.modifiers,
                ),
            )

    # Although I'm not particularly interested in this approach, but no much option because I lack the required mathematical skills to modify to my taste(math skills which i'm currently learning)
    # Therefore in the event it doesn't work out(The ad operation), Kindly revamp this scroll system
    def mouse_wheel_with_bezier_animation(self, x, y, px_to_adjust_by):
        plot = self.generate_mouse_wheel_curve(
            px_to_adjust_by, random.randint(1000, 4000)
        )
        for p in plot:
            self.webdriver.execute_cdp_cmd(
                "Input.dispatchMouseEvent",
                dict(
                    type="mouseWheel",
                    x=x,
                    y=y,
                    modifiers=self.keyboard.modifiers,
                    deltaX=0,
                    deltaY=p[1],
                ),
            )
            time.sleep(p[0])

    def mouse_wheel(self, x, y, px_to_adjust_by, is_reading=True, deltaX=0, deltaY=10):
        reading_pace = [90, 300]
        fast_scrolling_pace = [4, 35]
        scrolling_pace = [35, 80]

        latency = reading_pace

        latency = (latency[0] / 1000, latency[1] / 1000)

        self.x = x
        self.y = y

        if not is_reading:
            latency = fast_scrolling_pace
            if random.random() > 0.5:
                latency = scrolling_pace

        steps = int(px_to_adjust_by / deltaY)

        if steps == 0:
            steps == 1

        for i in range(steps):
            self.webdriver.execute_cdp_cmd(
                "Input.dispatchMouseEvent",
                dict(
                    type="mouseWheel",
                    x=x,
                    y=y,
                    modifiers=self.keyboard.modifiers,
                    deltaX=deltaX,
                    deltaY=deltaY,
                ),
            )
            time.sleep(random.uniform(latency[0], latency[1]))

    def click(self, x, y, options={"delay": 0}):
        delay = options["delay"]
        self.move(x, y)
        self.down(options)
        if delay:
            time.sleep(delay)
        self.up(options)

    def down(self, options={"button": "left", "click_count": 1}):
        button = options["button"]
        click_count = options["click_count"]
        self.button = button
        self.webdriver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            dict(
                type="mousePressed",
                button=button,
                x=self.x,
                y=self.y,
                modifiers=self.keyboard.modifiers,
                clickCount=click_count,
            ),
        )

    def up(self, options={"button": "left", "click_count": 1}):
        button = options["button"]
        click_count = options["click_count"]
        self.button = "none"
        self.webdriver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            dict(
                type="mouse_released",
                button=button,
                x=self.x,
                y=self.y,
                modifiers=self.keyboard.modifiers,
                clickCount=click_count,
            ),
        )


class Touchscreen:
    def __init__(self, webdriver: remote_webdriver.WebDriver, keyboard: Keyboard):
        self.webdriver = webdriver
        self.keyboard = keyboard

    def tap(self, x, y):
        # Touches appear to be lost during the first frame after navigation.
        # This waits a frame before sending the tap.
        # @see https:#crbug.com/613219
        # self.webdriver.execute_cdp_cmd('_runtime.evaluate', dict(
        #    expression='new Promise(x => requestAnimation_frame(() => requestAnimation_frame(x)))',
        #    awaitPromise=True
        # ))

        touch_points = [{"x": round(x), "y": round(y)}]
        print("tapped screen @:", touch_points)
        self.webdriver.execute_cdp_cmd(
            "Input.dispatchTouchEvent",
            dict(type="touchStart", touchPoints=touch_points),
        )
        time.sleep(random.uniform(0.01, 0.04))
        self.webdriver.execute_cdp_cmd(
            "Input.dispatchTouchEvent", dict(type="touchEnd", touchPoints=[])
        )

    def simulate_human_touch_movement_with_mouse(
        self, start_point=(0, 0), end_point=(0, 0), duration=3
    ):
        latency_range = (0.010, 0.025)
        duration += utils.fetch_percentage_value(duration, random.uniform(-10, 10))
        coords_distance = utils.find_points_distance_on_2d_cartesian_plane(
            start_point, end_point
        )
        target_points = round(
            utils.calculate_needed_points_from_coords_distance(
                coords_distance, (latency_range[0] + latency_range[1]) / 2, duration
            )
        )
        human_curve = HumanCurve(
            start_point, end_point, targetPoints=max(target_points, 2)
        )
        if start_point[0] > end_point[0]:
            left_boundary = end_point[0]
            right_boundary = start_point[0]
        else:
            left_boundary = start_point[0]
            right_boundary = end_point[0]

        if start_point[1] > end_point[1]:
            up_boundary = start_point[1]
            down_boundary = end_point[1]
        else:
            up_boundary = end_point[1]
            down_boundary = start_point[1]
        points = human_curve.generateCurve(
            offsetBoundaryX=40,
            offsetBoundaryY=0,
            leftBoundary=left_boundary,
            rightBoundary=right_boundary + 1,
            downBoundary=down_boundary,
            upBoundary=up_boundary + 1,
            distortionMean=0.2,
            distortionStdev=0.2,
            distortionFrequency=0.2,
            tweening=pytweening.linear,
            knotsCount=2,
            targetPoints=max(target_points, 2),
        )
        generated_durations = utils.generate_uniform_numbers_to_specific_range_and_sum(
            latency_range, target_points, duration
        )
        print("Generated Durations To Wait For: ", generated_durations[1])
        generated_durations = generated_durations[0]
        for i in range(len(points)):
            touch_points = [{"x": points[i][0], "y": points[i][1]}]
            if i == 0:
                self.webdriver.execute_cdp_cmd(
                    "Input.dispatchTouchEvent",
                    dict(
                        type="touchStart",
                        touchPoints=[{"x": points[0][0], "y": points[0][1]}],
                    ),
                )
            else:
                self.webdriver.execute_cdp_cmd(
                    "Input.dispatchTouchEvent",
                    dict(
                        type="touchMove",
                        touchPoints=touch_points,
                    ),
                )
            if i >= len(points) - 1:
                self.webdriver.execute_cdp_cmd(
                    "Input.dispatchTouchEvent",
                    dict(
                        type="touchEnd",
                        touchPoints=[],
                    ),
                )
            # Makes sure i is not out of index
            if i < len(generated_durations):
                time.sleep(generated_durations[i])
            else:
                time.sleep(random.choice(generated_durations))
        return True
