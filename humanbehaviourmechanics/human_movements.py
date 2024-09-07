import pytweening
import random
import asyncio
from threading import Thread

import pyautogui
from nodriver import Element as WebElement
from pyclick import HumanClicker, HumanCurve

from constants import bot_constants
from constants.keyboard_keys import Keys as K_Keys
from bots.devtools.devtools_input import Keyboard, Touchscreen, Mouse
from bots import utils


class HumanMovements:
    def __init__(self):
        self._keyboard = Keyboard(self.web_browser_driver)
        pyautogui.FAILSAFE = False
        self._touch = None
        if self.has_touch:
            self._touch = Touchscreen(self.web_browser_driver, self._keyboard)
        self._mouse = Mouse(self.web_browser_driver, self._keyboard)
        self.last_document_offsets = [0, 0]
        # No of clicks that could happen at the beginning of a scroll or touch scroll
        self.no_of_clicks = 0

        super().__init__()

    @property
    def keyboard(self):
        if self._keyboard and self._keyboard.web_browser_driver is None:
            self._keyboard.web_browser_driver = self.web_browser_driver
        return self._keyboard

    @property
    def mouse(self):
        if self._mouse and self._mouse.web_browser_driver is None:
            self._mouse.web_browser_driver = self.web_browser_driver
        return self._mouse

    @property
    def touch(self):
        if self._touch and self._touch.web_browser_driver is None:
            self._touch.web_browser_driver = self.web_browser_driver
        return self._touch

    @staticmethod
    async def get_mouse_position():
        return pyautogui.position()

    @staticmethod
    async def get_screen_size():
        return pyautogui.size()

    async def set_fail_safe(self, fail_safe_bool: bool):
        pyautogui.FAILSAFE = fail_safe_bool

    async def click_on_element(self, html_web_element):
        if isinstance(list, html_web_element):
            for ht_el in html_web_element:
                ht_el.click()
        else:
            html_web_element.click()

    async def simulate_human_mouse_move_behavior_to_area(
        self,
        x_coordinate,
        y_coordinate,
        area_width=1,
        area_height=1,
        probability_of_overshoot=0.0,
    ):
        """
        A Method To Simulate Human Mouse Behaviour To Specific Element On Screen. Powered By Pyclick and PyAutoGUI.
        Pass 1st and 2nd Argument To Click On a Specific Area. Pass Only The Next Six To Click On a Point Within an Area
        :param x_coordinate: The X coordinates On Screen Of Area
        If Clickable Area Exists, Make Sure It's Within Boundaries
        :param y_coordinate: The Y coordinates On Screen To Move Of Area.
        If Clickable Area Exists, Make Sure It's Within Boundaries
        :param area_width: The Surface Width of The Element You Want to Get To On Screen.
        :param area_height: The Surface Height of The Element You Want to Get To On Screen.
        :param probability_of_overshoot: Probability The Mouse Will Overshoot. 0 - Will Never Happen, 1 - Will Always Happen
        :return: coordinates moved to
        """
        if area_width > 1 and area_height > 1:
            x_coordinate = int(random.uniform(x_coordinate, area_width))
            y_coordinate = int(random.uniform(y_coordinate, area_height))

        return await self.simulate_human_mouse_move_behavior_to_point(
            x_coordinate, y_coordinate, probability_of_overshoot
        )

    async def simulate_human_mouse_move_behavior_to_point(
        self,
        x_coordinate,
        y_coordinate,
        probability_of_overshoot=1,
    ):
        """
        A Method To Simulate Human Mouse Behaviour To Specific Element On Screen. Powered By Pyclick and PyAutoGUI.
        Pass 1st and 2nd Argument To Click On a Specific Area. Pass Only The Next Six To Click On a Point Within an Area
        :param x_coordinate: The X coordinates On Screen To Move The Mouse To.
        If Clickable Area Exists, Make Sure It's Within Boundaries
        :param y_coordinate: The Y coordinates On Screen To Move The Mouse To.
        If Clickable Area Exists, Make Sure It's Within Boundaries
        :param probability_of_overshoot: Probability The Mouse Will Overshoot. 0 - Will Never Happen, 1 - Will Always Happen
        :return: Coordinates moved to
        """
        human_clicker = HumanClicker()
        human_curve = None
        human_curve = HumanCurve(
            pyautogui.position(),
            (x_coordinate, y_coordinate),
        )
        distance = int(
            utils.find_points_distance_on_2d_cartesian_plane(
                pyautogui.position(), (x_coordinate, y_coordinate)
            )
        )
        overshoot = 60
        if random.random() < probability_of_overshoot:
            overshoot += int(distance / 4 * random.uniform(0.8, 1.2))

        duration = random.uniform(0.2, 0.4 * (distance * 0.001))
        target_points = int(distance * 0.4 * random.uniform(0.8, 1.2))
        human_curve.points = human_curve.generateCurve(
            offsetBoundaryX=overshoot,
            offsetBoundaryY=overshoot,
            leftBoundary=x_coordinate,
            rightBoundary=x_coordinate,
            downBoundary=y_coordinate,
            upBoundary=y_coordinate,
            knotsCount=int(distance * 0.01 * random.uniform(0.8, 1.5)),
            distortionMean=0.2,
            distortionStdev=0.5,
            distortionFrequency=0.2,
            tween=pytweening.linear,
            targetPoints=target_points if target_points > 2 else 2,
        )

        human_clicker.move(
            (int(x_coordinate), int(y_coordinate)),
            humanCurve=human_curve,
            duration=duration,
        )

        print(
            f"Bot Process Id {self.bot_process_id} <:::> Mouse Moved To: ",
            x_coordinate,
            y_coordinate,
        )
        return {
            "x": int(x_coordinate),
            "y": int(y_coordinate),
        }

    async def move_pointing_device_to_element(
        self, html_web_element: WebElement, simulate_human_behaviour=True
    ):
        """
        :param html_web_element: HTML Element to Move To
        :param simulate_human_behaviour: If Bool is True(Which is By Default) use pyAutoGUI to Simulate Human Behaviour
        :return: return true on success
        """
        if simulate_human_behaviour:
            self.scroll_element_into_vertical_view(
                html_web_element, element_scroll_to=1
            )
            if not isinstance(self.touch, Touchscreen):
                element_screen_position = self.get_element_location_screen_offset(
                    html_web_element
                )
                el_pos = dict(
                    area_x=element_screen_position["html_web_element"]["x_offset"],
                    area_y=element_screen_position["html_web_element"]["y_offset"],
                    area_width=html_web_element.rect["width"],
                    area_height=html_web_element.rect["height"],
                )

                await self.simulate_human_mouse_move_behavior_to_area(
                    el_pos["area_x"] + 1,
                    el_pos["area_y"] + 1,
                    el_pos["area_width"] - 2,
                    el_pos["area_height"] - 2,
                    probability_of_overshoot=round(random.random(), 2),
                )
        else:
            html_web_element.scroll_into_view()

    async def scroll_to_percentage_in_element(
        self, html_web_element, percentage_to_scroll_to, time_to_sleep=1
    ):
        async def has_page_offset_changed():
            document_offsets = self.get_window_document_offsets()
            document_offsets = [
                document_offsets["x_offset"],
                document_offsets["y_offset"],
            ]
            if self.last_document_offsets == document_offsets:
                return False
            else:
                return True

        async def random_miscellaneous_key_presses(key_down_probability):
            for i in range(random.randint(1, 5)):
                if random.random() < key_down_probability:
                    self.keyboard.down(K_Keys["ArrowDown"])
                else:
                    self.keyboard.down(K_Keys["ArrowUp"])
                await asyncio.sleep(random.uniform(0.05, 0.45))

        async def scroll_with_touch(direction, duration):
            if direction:
                px_to_adjust_by = random.randint(1, 500)
            if not direction:
                px_to_adjust_by = random.randint(-500, -1)
            self.read_with_touch(px_to_adjust_by, duration)

        async def offset_adjuster(offset_to_adjust_to, html_web_element):
            element_coordinates = await self.get_element_location_window_offset(
                html_web_element
            )
            if offset_to_adjust_to > element_coordinates["y_offset"]:
                if isinstance(self.touch, Touchscreen):
                    while offset_to_adjust_to >= element_coordinates["y_offset"]:
                        if not has_page_offset_changed():
                            return True
                        scroll_with_touch(False, 0.5)
                        element_coordinates = self.get_element_location_window_offset(
                            html_web_element
                        )
                else:
                    while offset_to_adjust_to >= element_coordinates["y_offset"]:
                        asyncio.create_task(
                            self.keyboard.down_persistent(K_Keys["ArrowUp"])
                        )
                        if (
                            utils.clean_negative(element_coordinates["y_offset"])
                            - utils.clean_negative(offset_to_adjust_to)
                            < bot_constants.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT
                        ):
                            await asyncio.sleep(random.uniform(0.01, 0.267))
                            await self.keyboard.up(K_Keys["ArrowUp"])
                            await asyncio.sleep(random.uniform(0.15, 0.6))
                        else:
                            await asyncio.sleep(0.3)
                        element_coordinates = self.get_element_location_window_offset(
                            html_web_element
                        )
                    await self.keyboard.up(K_Keys["ArrowUp"])
                    if random.random() > 0.5:
                        await random_miscellaneous_key_presses(0.75)
            elif offset_to_adjust_to < element_coordinates["y_offset"]:
                if isinstance(self.touch, Touchscreen):
                    while offset_to_adjust_to <= element_coordinates["y_offset"]:
                        if not has_page_offset_changed():
                            return True
                        scroll_with_touch(True, 0.5)
                        element_coordinates = (
                            await self.get_element_location_window_offset(
                                html_web_element
                            )
                        )
                else:
                    while offset_to_adjust_to <= element_coordinates["y_offset"]:
                        asyncio.create_task(
                            self.keyboard.down_persistent(K_Keys["ArrowDown"])
                        )
                        if (
                            utils.clean_negative(offset_to_adjust_to)
                            - utils.clean_negative(element_coordinates["y_offset"])
                            < bot_constants.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT
                        ):
                            await asyncio.sleep(random.uniform(0.01, 0.267))
                            await self.keyboard.up(K_Keys["ArrowDown"])
                            await asyncio.sleep(random.uniform(0.15, 0.6))
                        else:
                            await asyncio.sleep(0.3)
                        element_coordinates = (
                            await self.get_element_location_window_offset(
                                html_web_element
                            )
                        )
                    await self.keyboard.up(K_Keys["ArrowDown"])
                    if random.random() > 0.5:
                        await random_miscellaneous_key_presses(0.25)

        # Element Height - Browser Window Makes It Possible To Eject Browser Dimensions From Calculations
        workable_height = (await html_web_element.get_position()).width - (
            await self.web_browser_driver.main_tab.get_window()
        )[1].height

        offset_to_adjust_to = utils.fetch_percentage_value(
            workable_height, percentage_to_scroll_to
        )
        offset_to_adjust_to *= -1

        original_y_offset = (
            await self.get_element_location_window_offset(html_web_element)
        )["y_offset"]

        await offset_adjuster(offset_to_adjust_to, html_web_element)
        await asyncio.sleep(time_to_sleep)
        await offset_adjuster(original_y_offset, html_web_element)

    async def read_with_arrow_keys(
        self,
        html_web_element,
        boundary,
        key=K_Keys["ArrowDown"],
        direction_to_move=True,
    ):
        asyncio.create_task(self.keyboard.down_persistent(key))
        element_coordinates = await self.get_element_location_window_offset(
            html_web_element
        )
        old_element_coordinates = element_coordinates
        boundary = (
            element_coordinates.get("y_offset") - boundary
            if direction_to_move
            else element_coordinates.get("y_offset") + boundary
        )
        offset_same_count = 0

        if direction_to_move:
            while element_coordinates.get("y_offset") >= boundary:
                old_element_coordinates = await self.get_element_location_window_offset(
                    html_web_element
                )
                await asyncio.sleep(0.3)
                element_coordinates = await self.get_element_location_window_offset(
                    html_web_element
                )

                if offset_same_count > 1:
                    break
                if element_coordinates.get("y_offset") == old_element_coordinates.get(
                    "y_offset"
                ):
                    offset_same_count += 1

        elif not direction_to_move:
            while boundary >= element_coordinates.get("y_offset"):
                old_element_coordinates = await self.get_element_location_window_offset(
                    html_web_element
                )
                await asyncio.sleep(0.3)
                element_coordinates = await self.get_element_location_window_offset(
                    html_web_element
                )

                if offset_same_count > 1:
                    break
                if element_coordinates.get("y_offset") == old_element_coordinates.get(
                    "y_offset"
                ):
                    offset_same_count += 1
        await self.keyboard.up(key)
        return True

    async def read_with_mouse_to_scrollbar(
        self,
        coordinates_offset_overshoot=dict(
            x=0,
            y=0,
            x_offset_percentage=0,
            y_offset_percentage=0,
            max_overshoot=0,
            probability_of_overshoot=0,
        ),
        is_asychronous=False,
        counter=0,
    ):
        pyautogui.mouseDown()
        if self.no_of_clicks > 0:
            while self.revert_to_main_page():
                pyautogui.mouseUp()
                pyautogui.mouseDown()

        asyncio.create_task(
            self.simulate_human_mouse_move_behavior_to_point(
                coordinates_offset_overshoot["x"],
                coordinates_offset_overshoot["y"],
                coordinates_offset_overshoot["probability_of_overshoot"],
            )
        )
        pyautogui.mouseUp()
        return counter

    async def read_with_touch(
        self, px_to_adjust_by, duration=random.uniform(0.1, 2), force_screen_reset=False
    ):
        # A List Containing The Browser's Page 9-Ways Splitted Dimension In The Following Format
        # [[(x, y, width, height) x3] x3]
        generated_page_boundaries = []
        if not hasattr(self, "generated_page_boundaries") or force_screen_reset:
            a_third_width = self.screen_width / 3
            a_third_height = self.screen_height / 3
            for h in range(3):
                generated_page_boundaries.append([])
                for w in range(3):
                    h_multiplier = h + 1
                    w_multiplier = w + 1
                    generated_page_boundaries[h].append(
                        (
                            a_third_width * w,
                            a_third_height * h,
                            a_third_width * w_multiplier,
                            a_third_height * h_multiplier,
                        )
                    )
            self.generated_page_boundaries = generated_page_boundaries
        else:
            generated_page_boundaries = self.generated_page_boundaries

        if random.uniform(0.0, 1.0) <= 0.95:
            y_start = random.randint(
                round(generated_page_boundaries[2][1][1]),
                round(generated_page_boundaries[2][1][3]),
            )
        else:
            if random.random() == 0:
                y_start = random.randint(
                    round(generated_page_boundaries[0][1][1]),
                    round(generated_page_boundaries[0][1][3]),
                )
            else:
                y_start = random.randint(
                    round(generated_page_boundaries[1][1][1]),
                    round(generated_page_boundaries[1][1][3]),
                )

        if random.uniform(0.0, 1.0) <= 0.95:
            x_start = random.randint(
                round(generated_page_boundaries[2][1][0]),
                round(generated_page_boundaries[2][1][2]),
            )
        else:
            if random.random() == 0:
                x_start = random.randint(
                    round(generated_page_boundaries[2][0][0]),
                    round(generated_page_boundaries[2][0][2]),
                )
            else:
                x_start = random.randint(
                    round(generated_page_boundaries[2][2][0]),
                    round(generated_page_boundaries[2][2][2]),
                )
        y_end = round(y_start - px_to_adjust_by)
        x_end = round(
            x_start + utils.fetch_percentage_value(x_start, random.uniform(-4, 4))
        )

        x_start = x_start if x_start >= 0 else 0
        y_start = y_start if y_start >= 0 else 0
        x_end = x_end if x_end >= 0 else 0
        y_end = y_end if y_end >= 0 else 0

        await self.touch.simulate_human_touch_movement_with_mouse(
            (x_start, y_start), (x_end, y_end), duration
        )

        await self.smart_click_trigger((x_start, y_start), self.device_type)

    async def scroll_element_into_vertical_view(
        self,
        html_web_element: WebElement,
        element_scroll_to=1,
        simulate_human_behaviour=True,
    ):
        """
        This Method Scrolls The Web Page To Put Requested Web Element In View
        :param html_web_element: HTML Web Element To Scroll To
        :param element_scroll_to: Scroll To Top Or Bottom Of Element 1: 0 For Top, 1 For Bottom
        :param simulate_human_behaviour: If Argument Is True, Method Will Attempt To Simulate Human Interaction Scroll
        :return: Return True When Scroll Is Complete
        """

        async def has_page_offset_changed():
            document_offsets = await self.get_window_document_offsets()
            document_offsets = [
                document_offsets["x_offset"],
                document_offsets["y_offset"],
            ]
            if self.last_document_offsets == document_offsets:
                return False
            else:
                return True

        async def scroll(key, direction):
            """
            Use Directional Keys To Scroll To Element
            :return: True
            """
            if random.random() < 0.85:
                await self.mouse.mouse_wheel(
                    *pyautogui.position(),
                    random.randint(10, 100),
                    is_reading=False,
                    deltaY=self.identity.mouse_delta_y,
                    yDirection=direction,
                )
            else:
                asyncio.create_task(self.keyboard.down_persistent(key))
                await asyncio.sleep(random.uniform(1.1, 1.75))
                await self.keyboard.up(key)
                await asyncio.sleep(random.uniform(0.5, 1.5))

        async def scroll_with_touch(direction, duration):
            if direction:
                px_to_adjust_by = random.randint(1, 500)
            if not direction:
                px_to_adjust_by = random.randint(-500, -1)
            await self.read_with_touch(px_to_adjust_by, duration)

        element_browser_coordinates = await self.get_element_location_screen_offset(
            html_web_element
        )

        if simulate_human_behaviour:
            if element_scroll_to == 0:
                if (
                    element_browser_coordinates["html_web_element"]["y_offset"]
                    > element_browser_coordinates["browser_window_rect"][1]
                ):
                    while (
                        element_browser_coordinates["html_web_element"]["y_offset"]
                        >= element_browser_coordinates["browser_window_rect"][1]
                    ):
                        if isinstance(self.touch, Touchscreen):
                            await scroll_with_touch(True, 1)
                        else:
                            await scroll(K_Keys["ArrowDown"], True)
                        if not await has_page_offset_changed():
                            return True
                        element_browser_coordinates = (
                            await self.get_element_location_screen_offset(
                                html_web_element
                            )
                        )
                elif (
                    element_browser_coordinates["html_web_element"]["y_offset"]
                    < element_browser_coordinates["browser_window_rect"][1]
                ):
                    while (
                        element_browser_coordinates["html_web_element"]["y_offset"]
                        <= element_browser_coordinates["browser_window_rect"][1]
                    ):
                        if isinstance(self.touch, Touchscreen):
                            await scroll_with_touch(False, 1)
                        else:
                            await scroll(K_Keys["ArrowUp"], False)
                        if not await has_page_offset_changed():
                            return True
                        element_browser_coordinates = (
                            await self.get_element_location_screen_offset(
                                html_web_element
                            )
                        )

            elif element_scroll_to == 1:
                if (
                    element_browser_coordinates["html_web_element"]["bottom"]
                    > element_browser_coordinates["browser_window_rect"][2]
                ):
                    while (
                        element_browser_coordinates["html_web_element"]["bottom"]
                        >= element_browser_coordinates["browser_window_rect"][2]
                    ):
                        if isinstance(self.touch, Touchscreen):
                            await scroll_with_touch(True, 1)
                        else:
                            await scroll(K_Keys["ArrowDown"])
                        if not has_page_offset_changed():
                            return True
                        element_browser_coordinates = (
                            self.get_element_location_screen_offset(html_web_element)
                        )
                elif (
                    element_browser_coordinates["html_web_element"]["y_offset"]
                    < element_browser_coordinates["browser_window_rect"][1]
                ):
                    while (
                        element_browser_coordinates["html_web_element"]["y_offset"]
                        <= element_browser_coordinates["browser_window_rect"][1]
                    ):
                        if isinstance(self.touch, Touchscreen):
                            await scroll_with_touch(False, 1)
                        else:
                            await scroll(K_Keys["ArrowUp"])
                        if not has_page_offset_changed():
                            return True
                        element_browser_coordinates = (
                            self.get_element_location_screen_offset(html_web_element)
                        )

        else:
            await html_web_element.scroll_into_view()

    async def send_mouse_to_scrollbar(self, is_asychronous=False):
        scroll_bar = self.get_scroll_bar_coordinates(2)
        return asyncio.create_task(
            self.simulate_human_mouse_move_behavior_to_area(
                scroll_bar["x_pos"] + 2,
                scroll_bar["y_pos"] + 2,
                scroll_bar["width"],
                scroll_bar["height"],
                random.uniform(0.4, 1.0),
            )
        )

    async def click_trigger(self, x_coord=50, y_coord=50, device_type="computer"):
        if device_type == "is_smartphone":
            self.human_movements.touch.tap(x_coord, y_coord)
            return True
        elif device_type == "computer":
            pyautogui.click()
            return True
        else:
            print(
                f"Bot Process Id {self.bot_process_id} <:::> The device type you are attempting to click on is unknown"
            )
            return False

    async def smart_click_trigger(self, coordinates=(100, 100), device_type="computer"):
        if self.no_of_clicks > 0:
            if random.uniform(0, 1) <= self.probability_of_click:
                self.probability_of_click -= utils.fetch_percentage_value(
                    self.probability_of_click, 15
                )
                self.no_of_clicks -= 1
                self.click_trigger(coordinates[0], coordinates[1], device_type)
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> Click was triggered successfully"
                )
                return True
            else:
                self.probability_of_click += utils.fetch_percentage_value(
                    self.probability_of_click, 15
                )
                return False
        return False
