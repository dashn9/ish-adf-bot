import random
import asyncio
from threading import Thread

import pytweening
from nodriver import cdp, Browser
from constants.keyboard_keys import Keys
from pyclick import HumanCurve

from bots import utils


class Keyboard:
    def __init__(self, web_browser_driver: Browser):
        self.web_browser_driver = web_browser_driver
        self.modifiers = 0
        self.is_key_down = False
        self.down_key_number_of_consecutive_runs = 0
        self.pressed_keys = set()

    async def down(self, key, options={"text": "", "keypad": False}, simple=False):
        description = await self.key_description_for_string(key)

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
        await self.web_browser_driver.main_tab.send(
            cdp.input_.dispatch_key_event(
                type_=type,
                modifiers=self.modifiers,
                windows_virtual_key_code=description["key_code"],
                code=description["code"],
                key=description["key"],
                text=text,
                unmodified_text=text,
                auto_repeat=auto_repeat,
                location=description["location"],
                is_keypad=is_keypad,
            )
        )

    async def down_persistent(self, key, options={"text": ""}):
        if not self.is_key_down:
            self.is_key_down = True
            try:
                await self.down(key, options, True)
                await asyncio.sleep(random.uniform(0.5, 0.52))
                while self.is_key_down:
                    await self.down(key, options, True)
                    await asyncio.sleep(random.uniform(0.04, 0.07))
                    # self.down_key_number_of_consecutive_runs += 1
                self.down_key_number_of_consecutive_runs = 0
            except Exception:
                pass

    async def modifier_bit(self, key):
        if key == "Alt":
            return 1
        if key == "Control":
            return 2
        if key == "Meta":
            return 4
        if key == "Shift":
            return 8
        return 0

    async def key_description_for_string(self, key):
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

    async def up(self, key):
        description = await self.key_description_for_string(key)
        self.modifiers &= ~(await self.modifier_bit(description["key"]))
        if self.is_key_down:
            self.is_key_down = False
            self.pressed_keys.discard(description["code"])

            while self.down_key_number_of_consecutive_runs != 0:
                await asyncio.sleep(0.1)

            await self.web_browser_driver.main_tab.send(
                cdp.input_.dispatch_key_event(
                    type_="keyUp",
                    modifiers=self.modifiers,
                    key=description["key"],
                    windows_virtual_key_code=description["key_code"],
                    code=description["code"],
                    location=description["location"],
                ),
            )

    async def send_character(self, char: str):
        await self.web_browser_driver.main_tab.send(cdp.input_.insert_text(text=char))

    async def type(self, text: str, options={"delay": 0}):
        delay = 0
        if options and options.delay:
            delay = options.delay
        for char in text:
            if Keys[char]:
                self.press(char, {delay})
            else:
                self.send_character(char)
            if delay:
                await asyncio.sleep(delay)

    async def press(self, key, options=(0,)):
        delay = options
        self.down(key, options)
        if delay:
            await asyncio.sleep(delay)
        self.up(key)


class Mouse:
    def __init__(self, web_browser_driver: Browser, keyboard: Keyboard):
        self.web_browser_driver = web_browser_driver
        self.keyboard = keyboard
        self.x = 0
        self.y = 0

    async def move(self, x, y, options={"steps": 10}):
        steps = options["steps"]
        from_x = self.x
        from_y = self.y
        self.x = x
        self.y = y
        for i in range(steps):
            await self.web_browser_driver.main_tab.send(
                cdp.input_.dispatch_mouse_event(
                    type_="mouseMoved",
                    x=from_x + (self.x - from_x) * (i / steps),
                    y=from_y + (self.y - from_y) * (i / steps),
                    modifiers=self.keyboard.modifiers,
                )
            )

    # Although I'm not particularly interested in this approach, but no much option because I lack the required mathematical skills to modify to my taste(math skills which i'm currently learning)
    # Therefore in the event it doesn't work out(The ad operation), Kindly revamp this scroll system
    async def mouse_wheel_with_bezier_animation(
        self, x, y, px_to_adjust_by, yDirection=True
    ):
        plot = utils.generate_mouse_wheel_plot(
            int(px_to_adjust_by), random.randint(50, 200)
        )
        for p in plot:
            await self.web_browser_driver.main_tab.send(
                cdp.input_.dispatch_mouse_event(
                    type_="mouseWheel",
                    x=x,
                    y=y,
                    modifiers=self.keyboard.modifiers,
                    delta_x=0,
                    delta_y=p[1] if yDirection else -p[1],
                )
            )
            await asyncio.sleep(p[0] / 1000)

    # Irrespective, a huge load of optimizations is still needed here after brushing my math and bitwise skills
    async def mouse_wheel(
        self,
        x,
        y,
        px_to_adjust_by,
        is_reading=True,
        deltaX=0,
        deltaY=10,
        vary_deltaY_on_read=False,
        yDirection=True,
    ):
        reading_pace = [0.7, 3]
        fast_scrolling_pace = [0.08, 0.7]
        scrolling_pace = [0.7, 1.6]

        latency = reading_pace

        self.x = x
        self.y = y

        if not is_reading:
            latency = fast_scrolling_pace
            if random.random() > 0.5:
                latency = scrolling_pace

        latency = [latency[0] * deltaY, latency[1] * deltaY]

        steps = int(px_to_adjust_by / deltaY)

        if steps == 0:
            steps == 1

        vary_deltaY_on_read = vary_deltaY_on_read and is_reading
        for i in range(steps):
            deltaY_modifier = 1
            prob_of_restep = random.random()
            if vary_deltaY_on_read and prob_of_restep >= 0.80:
                deltaY_modifier += 1
                i += 1
            if vary_deltaY_on_read and prob_of_restep >= 0.87:
                deltaY_modifier += 1
                i += 1
            deltaYToUse = deltaY * deltaY_modifier
            await self.web_browser_driver.main_tab.send(
                cdp.input_.dispatch_mouse_event(
                    type_="mouseWheel",
                    x=x,
                    y=y,
                    modifiers=self.keyboard.modifiers,
                    delta_x=deltaX,
                    delta_y=deltaYToUse if (yDirection) else -deltaYToUse,
                )
            )
            await asyncio.sleep(random.uniform(latency[0], latency[1]) / 1000)

    async def click(self, x, y, options={"delay": 0}):
        delay = options["delay"]
        self.move(x, y)
        self.down(options)
        if delay:
            await asyncio.sleep(delay)
        self.up(options)

    async def down(self, options={"button": "left", "click_count": 1}):
        button = options["button"]
        click_count = options["click_count"]
        self.button = button
        await self.web_browser_driver.main_tab.send(
            cdp.input_.dispatch_mouse_event(
                type_="mousePressed",
                button=button,
                x=self.x,
                y=self.y,
                modifiers=self.keyboard.modifiers,
                click_count=click_count,
            )
        )

    async def up(self, options={"button": "left", "click_count": 1}):
        button = options["button"]
        click_count = options["click_count"]
        self.button = "none"
        await self.web_browser_driver.main_tab.send(
            cdp.input_.dispatch_mouse_event(
                type_="mouseReleased",
                button=button,
                x=self.x,
                y=self.y,
                modifiers=self.keyboard.modifiers,
                click_count=click_count,
            ),
        )


class Touchscreen:
    def __init__(self, web_browser_driver: Browser, keyboard: Keyboard):
        self.web_browser_driver = web_browser_driver
        self.keyboard = keyboard

    async def tap(self, x, y):
        # Touches appear to be lost during the first frame after navigation.
        # This waits a frame before sending the tap.
        # @see https:#crbug.com/613219
        # await self.web_browser_driver.main_tab.send('_runtime.evaluate', dict(
        #    expression='new Promise(x => requestAnimation_frame(() => requestAnimation_frame(x)))',
        #    awaitPromise=True
        # ))

        touch_points = [{"x": round(x), "y": round(y)}]
        print("tapped screen @:", touch_points)
        await self.web_browser_driver.main_tab.send(
            cdp.input_.dispatch_touch_event(
                type_="touchStart", touch_points=touch_points
            )
        )
        await asyncio.sleep(random.uniform(0.01, 0.04))
        await self.web_browser_driver.main_tab.send(
            cdp.input_.dispatch_touch_event(type_="touchEnd", touch_points=[])
        )

    async def simulate_human_touch_movement_with_mouse(
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
                await self.web_browser_driver.main_tab.send(
                    cdp.input_.dispatch_touch_event(
                        type_="touchStart",
                        touch_points=[{"x": points[0][0], "y": points[0][1]}],
                    )
                )
            else:
                await self.web_browser_driver.main_tab.send(
                    cdp.input_.dispatch_touch_event(
                        type_="touchMove",
                        touch_points=touch_points,
                    )
                )
            if i >= len(points) - 1:
                await self.web_browser_driver.main_tab.send(
                    cdp.input_.dispatch_touch_event(
                        type_="touchEnd",
                        touch_points=[],
                    )
                )
            # Makes sure i is not out of index
            if i < len(generated_durations):
                await asyncio.sleep(generated_durations[i])
            else:
                await asyncio.sleep(random.choice(generated_durations))
        return True
