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
from log import logger


class HumanMovements:
    def __init__(self, no_of_clicks=0):
        self._keyboard = Keyboard(self)
        pyautogui.FAILSAFE = False
        self._touch = None
        if self.identity.has_touch:
            self._touch = Touchscreen(self, self._keyboard)
        self._mouse = Mouse(self, self._keyboard)
        self.last_document_offsets = [0, 0]
        # No of clicks that could happen at the beginning of a scroll or touch scroll
        self.no_of_clicks = no_of_clicks

        super().__init__()

    @property
    def keyboard(self):
        if self._keyboard and self._keyboard.webbot is None:
            self._keyboard.webbot = self
        return self._keyboard

    @property
    def mouse(self):
        if self._mouse and self._mouse.webbot is None:
            self._mouse.webbot = self
        return self._mouse

    @property
    def touch(self):
        if self._touch and self._touch.webbot is None:
            self._touch.webbot = self
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
            await self.scroll_element_into_vertical_view(
                html_web_element, element_scroll_to=1
            )
            if not isinstance(self.touch, Touchscreen):
                element_screen_position = await self.get_element_location_screen_offset(
                    html_web_element
                )
                el_pos = dict(
                    area_x=element_screen_position["html_web_element"]["x_offset"],
                    area_y=element_screen_position["html_web_element"]["y_offset"],
                    area_width=element_screen_position["html_web_element"]["width"],
                    area_height=element_screen_position["html_web_element"]["height"],
                )

                await self.simulate_human_mouse_move_behavior_to_area(
                    el_pos["area_x"] + 1,
                    el_pos["area_y"] + 1,
                    el_pos["area_x"] + el_pos["area_width"] - 2,
                    el_pos["area_y"] + el_pos["area_height"] - 2,
                    probability_of_overshoot=round(random.random(), 2),
                )
        else:
            html_web_element.scroll_into_view()

    async def scroll_to_percentage_in_element(
        self, html_web_element, percentage_to_scroll_to, time_to_sleep=None
    ):
        document_bounds = await self.get_window_document_bounds()

        last_element_position = None

        async def has_element_offset_changed():
            nonlocal last_element_position
            logger.info("{{{ Checking If Document Offsets Changed }}}")
            new_position = await html_web_element.get_position()
            if last_element_position == new_position:
                logger.info("{{{ Element Position Did Not Change }}}")
                return False
            else:
                logger.info("{{{ Element Position Changed }}}")
                last_element_position = new_position
                return True

        async def scroll_with_touch(direction, duration):
            if direction:
                px_to_adjust_by = random.randint(1, 450)
            if not direction:
                px_to_adjust_by = random.randint(-450, -1)
            await self.read_with_touch(px_to_adjust_by, duration)

        async def scroll(direction):
            if self.touch:
                logger.info("<--> Scrolling To Percentage In Element With Touch <-->")
                await scroll_with_touch(direction, 0.5)
            else:
                if random.random() <= 0.9:
                    logger.info(
                        "<--> Scrolling To Percentage In Element With Mouse Wheel <-->"
                    )
                    await self.mouse.mouse_wheel_with_bezier_animation(
                        *pyautogui.position(), random.randint(1, 600), direction
                    )
                else:
                    # seperate into config
                    logger.info(
                        "<--> Scrolling To Percentage In Element With Arrow Keys <-->"
                    )
                    await self.read_with_arrow_keys(
                        random.randint(
                            200,
                            int(
                                self.identity.screen_resolution.get("logical_height")
                                * 1.5
                            ),
                        ),
                        direction,
                    )

        async def offset_adjuster(offset_to_adjust_to):
            """When scrolling, if the px to adjust to goes within bounds of the document, an infinite scroll will occur, I don't want to complicate, so I shall stick with detecting and exiting"""
            nonlocal document_bounds
            if offset_to_adjust_to > document_bounds.get("bottom"):
                while offset_to_adjust_to > document_bounds.get("bottom"):
                    logger.info(
                        f"<--> Offsetting Downwards To: {offset_to_adjust_to} From {document_bounds.get('bottom')} <-->"
                    )
                    if not (await has_element_offset_changed()):
                        return True
                    await scroll(True)
                    document_bounds = await self.get_window_document_bounds()
            else:
                while offset_to_adjust_to < document_bounds.get("y_offset"):
                    logger.info(
                        f"<--> Offsetting Upwards To: {offset_to_adjust_to} From {document_bounds.get('y_offset')} <-->"
                    )
                    if not (await has_element_offset_changed()):
                        return True
                    await scroll(False)
                    document_bounds = await self.get_window_document_bounds()

        element_bounds = await html_web_element.get_position()
        curr_window_y_offset = (await self.get_window_document_offsets()).get(
            "y_offset"
        )
        offset_to_adjust_to = (
            utils.fetch_percentage_value(element_bounds.height, percentage_to_scroll_to)
            + element_bounds.y
            + curr_window_y_offset
        )
        logger.info(
            f"<--> Setting Up Adjustment To Element's Top: {element_bounds.y} On Height: {element_bounds.height}"
        )
        await offset_adjuster(offset_to_adjust_to)
        logger.info("<--> Done Scrolling to Percentage in Element <-->")
        if time_to_sleep is not None:
            logger.info("<--> Sleeping... <-->")
            await asyncio.sleep(time_to_sleep)
            logger.info("<--> Returning To Original Position... <-->")
            await offset_adjuster(curr_window_y_offset)

    async def read_with_arrow_keys(
        self,
        boundary,
        direction,
    ):
        doc_boundary = await self.get_window_document_bounds()
        logger.info(
            f"<--> Arrow Keys Read: Document Offset Currently At: {doc_boundary.get('y_offset')} <-->",
        )
        key = K_Keys["ArrowDown"]
        if not direction:
            key = K_Keys["ArrowUp"]
            boundary = doc_boundary["bottom"] - boundary
        else:
            boundary = doc_boundary["y_offset"] + boundary
        asyncio.create_task(self.keyboard.down_persistent(key))

        while doc_boundary["y_offset"] < boundary and direction:
            await asyncio.sleep(0.3)
            _doc_boundary = await self.get_window_document_bounds()
            if _doc_boundary == doc_boundary:
                logger.info(
                    f"<--> Arrow Keys Read: Operation Seems To Have Hit Max Bounds, Can't Go Any Further Breaking... <-->"
                )
                break
            doc_boundary = _doc_boundary
            logger.info(
                f"<--> Arrow Keys Read: Going Down :: {doc_boundary.get('y_offset')} <-->"
            )

        while doc_boundary["bottom"] > boundary and not direction:
            await asyncio.sleep(0.3)
            _doc_boundary = await self.get_window_document_bounds()
            if _doc_boundary == doc_boundary:
                logger.info(
                    f"<--> Arrow Keys Read: Operation Seems To Have Hit Max Bounds, Can't Go Any Further Breaking... <-->"
                )
                break
            doc_boundary = _doc_boundary
            logger.info(
                f"<--> Arrow Keys Read: Going Up :: {doc_boundary.get('y_offset')} <-->"
            )

        await self.keyboard.up(key)
        logger.info("<--> Arrow Keys Read: Done <-->")
        return True

    async def read_with_touch(
        self, px_to_adjust_by, duration=None, force_screen_reset=False
    ):
        """Requires heavy rethink and rework"""
        # In the future, take this of to config
        duration = duration or random.uniform(0.1, 3)

        logger.info(f"<--> Touch Read: Reading :: To Adjust By: {px_to_adjust_by} <-->")
        if abs(px_to_adjust_by) < 100:
            logger.warning(
                f"<--> Touch Read: Reading :: To Adjust By: {px_to_adjust_by} is Undesirable, Resetting... <-->"
            )
            px_to_adjust_by = 100 * (1 if px_to_adjust_by >= 0 else -1)
        # A List Containing The Browser's Page 9-Ways Splitted Dimension In The Following Format
        # [[(x, y, width, height) x3] x3]
        generated_page_boundaries = []
        if not hasattr(self, "generated_page_boundaries") or force_screen_reset:
            logger.info("<--> Touch Read: Generating Page Boundaries <-->")
            a_third_width = self.identity.screen_resolution.get("logical_width") / 3
            a_third_height = self.identity.screen_resolution.get("logical_height") / 3
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
            logger.info("<--> Touch Read: Saving Generated Page Boundaries <-->")
            self.generated_page_boundaries = generated_page_boundaries
        else:
            logger.info("<--> Touch Read: Reusing Generated Page Boundaries <-->")
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

        logger.info(f"<--> Touch Read : : ({x_start,y_start}), ({x_end,y_end}) <-->")

        logger.info(
            "<--> Touch Read: Simualating Human Touch Movement With Mouse... <-->"
        )
        await self.touch.simulate_human_touch_movement_with_mouse(
            (x_start, y_start), (x_end, y_end), duration
        )
        logger.info("<--> Engaging Smart Click Trigger <-->")
        await self.smart_click_trigger((x_start, y_start), self.identity.device_type)

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
        if simulate_human_behaviour:
            await self.scroll_to_percentage_in_element(
                html_web_element, 100 if element_scroll_to else 0.01
            )
        else:
            await html_web_element.scroll_into_view()

    async def click_trigger(self, x_coord=50, y_coord=50, device_type="computer"):
        if device_type == "smartphone":
            await self.touch.tap(x_coord, y_coord)
            return True
        elif device_type == "computer":
            pyautogui.click()
            return True
        else:
            print(
                f"Bot Process Id {self.bot_process_id} <:::> The device type you are attempting to click on is unknown"
            )
            return False

    # Look at this function when you decide to make use of popunders in prod
    async def smart_click_trigger(
        self, coordinates=(100, 100), device_type="computer", probability=None
    ):
        if self.no_of_clicks > 0:
            if random.random() <= (probability or self.probability_of_click):
                # Mistake Triggering Ad is more common on Smartphone because of popunder is more common
                if (
                    not device_type == "computer"
                    and (await self.trigger_vignette()) == True
                ):
                    logger.info(
                        "<--> Won't Trigger Click Because A Vignette Ad Was Present And Closed <-->"
                    )
                    return False
                self.probability_of_click -= utils.fetch_percentage_value(
                    self.probability_of_click, 15
                )
                self.no_of_clicks -= 1
                await self.click_trigger(coordinates[0], coordinates[1], device_type)
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> Click was triggered successfully"
                )
                await self.revert_to_active_page(
                    time_interval_to_check=random.uniform(1.5, 4)
                )
                return True
            else:
                self.probability_of_click += utils.fetch_percentage_value(
                    self.probability_of_click, 15
                )
                return False
        return False
