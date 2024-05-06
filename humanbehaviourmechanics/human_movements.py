import pytweening
import random
import time

import pyautogui
from selenium.webdriver.remote.webdriver import WebElement
from threading import Thread
from pyclick import HumanClicker, HumanCurve

from browsers.browser_interface import BrowserInterface
from constants import bot_constants
from constants.keyboard_keys import Keys as K_Keys
from bots.devtools.devtools_input import Keyboard, Touchscreen
from bots import utils
from humanbehaviourmechanics.smart_ads_interactions import SmartAdsInteractions


class HumanMovements:
    def __init__(self, browser_interface: BrowserInterface, smart_ads_interactions=None, mouse_delta_y=50):
        self.browser_interface = browser_interface
        self.keyboard = Keyboard(self.browser_interface.web_browser_driver)
        pyautogui.FAILSAFE = False
        if self.browser_interface.has_touch == "has_touch":
            self.touch = Touchscreen(self.browser_interface.web_browser_driver, self.keyboard)
        self.mouse = None
        self.bot_process_id = browser_interface.bot_process_id
        self.last_document_offsets = [0, 0]
        self.mouse_delta_y = mouse_delta_y
        self.smart_ads_interactions = smart_ads_interactions

        super().__init__()

    @staticmethod
    def get_mouse_position():
        return pyautogui.position()

    @staticmethod
    def get_screen_size():
        return pyautogui.size()

    def set_fail_safe(self, fail_safe_bool: bool):
        pyautogui.FAILSAFE = fail_safe_bool

    def click_on_element(self, html_web_element):
        if isinstance(list, html_web_element):
            for ht_el in html_web_element:
                ht_el.click()
        else:
            html_web_element.click()

    def simulate_human_mouse_move_behavior_to_area(
            self, x_coordinates, y_coordinates, area_width=1, area_height=1,
            x_coordinates_offset_percentage=0, y_coordinates_offset_percentage=0, max_overshoot=0,
            probability_of_overshoot=0.0, is_small_distance=False, move_to_new_thread=False):
        """
        A Method To Simulate Human Mouse Behaviour To Specific Element On Screen. Powered By Pyclick and PyAutoGUI.
        Pass 1st and 2nd Argument To Click On a Specific Area. Pass Only The Next Six To Click On a Point Within an Area
        :param x_coordinates: The X coordinates On Screen Of Area
        If Clickable Area Exists, Make Sure It's Within Boundaries
        :param y_coordinates: The Y coordinates On Screen To Move Of Area.
        If Clickable Area Exists, Make Sure It's Within Boundaries
        :param area_width: The Surface Width of The Element You Want to Get To On Screen.
        :param area_height: The Surface Height of The Element You Want to Get To On Screen.
        :param x_coordinates_offset_percentage:
        By How Many Percent Deviation To Move From The X Coordinates In Relation To Area Width.
        Max is 100%
        :param y_coordinates_offset_percentage:
        By How Many Percent Deviation To Move From The Y Coordinates In Relation To Area Height
        Max is 100%
        :param max_overshoot: A Random Percentage Number Will Be Generated Not Greater Than The Value For Both X and Y
        Coordinates Which Will Make The Mouse Overshoot Beyond The Set Coordinates and Back. Max is 100%
        :param probability_of_overshoot: Probability The Mouse Will Overshoot. 0 - Will Never Happen, 1 - Will Always Happen
        :param is_small_distance: Advisable To Set To True If ToMoveTo From Mouse Original Position Is Not Far Apart
        :param move_to_new_thread: Move Operations To Another Thread, If True
        :return: True When Done
        """
        screen_size = pyautogui.size()
        if x_coordinates >= screen_size[0]:
            x_coordinates = screen_size[0] - 2
        if y_coordinates >= screen_size[1]:
            y_coordinates = screen_size[1] - 2

        def move_operations():
            x_coordinates_to_move_to, y_coordinates_to_move_to = x_coordinates, y_coordinates

            # If Offset Percentages Are Set and Area Width And Height is Given
            if (x_coordinates_offset_percentage > 0 and y_coordinates_offset_percentage > 0 and
                    area_width > 1 and area_height > 1):
                # Calculate Offsets Based On Percentages
                x_coordinates_to_move_to = (
                                                   area_width * x_coordinates_offset_percentage / 100) + x_coordinates_to_move_to
                y_coordinates_to_move_to = (
                                                   area_height * y_coordinates_offset_percentage / 100) + y_coordinates_to_move_to

                # If x_coordinates To Click On, Extends Beyond Width Bounds, Set To Bounds Point
                if x_coordinates_to_move_to < x_coordinates or x_coordinates_to_move_to > x_coordinates + area_width:
                    x_coordinates_to_move_to = x_coordinates + (area_width / 2)

                # If y_coordinates To Click On, Extends Beyond Height Bounds, Set To Bounds Point
                if y_coordinates_to_move_to < y_coordinates or y_coordinates_to_move_to > y_coordinates + area_height:
                    y_coordinates_to_move_to = y_coordinates + (area_height / 2)

            self.human_clicker = HumanClicker()

            human_curve = None
            duration = random.uniform(0.2, 1.2)
            if is_small_distance:
                x_coordinates_to_move_to = int(x_coordinates_to_move_to)
                y_coordinates_to_move_to = int(y_coordinates_to_move_to)
                human_curve = HumanCurve(pyautogui.position(), (x_coordinates_to_move_to, y_coordinates_to_move_to),
                                         targetPoints=50)
                human_curve.points = human_curve.generateCurve(offsetBoundaryX=0, offsetBoundaryY=0,
                                                               leftBoundary=x_coordinates_to_move_to,
                                                               rightBoundary=x_coordinates_to_move_to + 1,
                                                               downBoundary=y_coordinates_to_move_to,
                                                               upBoundary=y_coordinates_to_move_to + 1,
                                                               knotsCount=5,
                                                               distortionMean=0.4, distortionStdev=0.2,
                                                               distortionFrequency=0.2,
                                                               tween=pytweening.linear,
                                                               targetPoints=50)
            if probability_of_overshoot > 0.5:
                self.human_clicker.move((int(x_coordinates_to_move_to + (
                        x_coordinates_to_move_to * random.randint(-max_overshoot, max_overshoot) / 100)),
                                         int(y_coordinates_to_move_to + (
                                                 y_coordinates_to_move_to * random.randint(-max_overshoot,
                                                                                           max_overshoot) / 100))),
                                        humanCurve=human_curve, duration=duration)
            self.human_clicker.move((int(x_coordinates_to_move_to), int(y_coordinates_to_move_to)),
                                    humanCurve=human_curve, duration=duration)

            print(f"Bot Process Id {self.bot_process_id} <:::> Mouse Moved To Area Point: ", x_coordinates_to_move_to,
                  y_coordinates_to_move_to)
            return {'x': int(x_coordinates_to_move_to), 'y': int(y_coordinates_to_move_to)}

        if move_to_new_thread:
            t = Thread(target=move_operations)
            t.daemon = True
            return t.start()
        else:
            return move_operations()

    def simulate_human_mouse_move_behavior_to_point(
            self, x_coordinates, y_coordinates, x_coordinates_offset_percentage=0, y_coordinates_offset_percentage=0,
            max_overshoot=0, probability_of_overshoot=0.0, is_small_distance=False, move_to_new_thread=False):
        """
        A Method To Simulate Human Mouse Behaviour To Specific Element On Screen. Powered By Pyclick and PyAutoGUI.
        Pass 1st and 2nd Argument To Click On a Specific Area. Pass Only The Next Six To Click On a Point Within an Area
        :param x_coordinates: The X coordinates On Screen To Move The Mouse To.
        If Clickable Area Exists, Make Sure It's Within Boundaries
        :param y_coordinates: The Y coordinates On Screen To Move The Mouse To.
        If Clickable Area Exists, Make Sure It's Within Boundaries
        :param x_coordinates_offset_percentage:
        By How Many Percent Deviation To Move From The X Coordinates In Relation To Area Width.
        Max is 100%
        :param y_coordinates_offset_percentage:
        By How Many Percent Deviation To Move From The Y Coordinates In Relation To Area Height
        Max is 100%
        :param max_overshoot: A Random Percentage Number Will Be Generated Not Greater Than The Value For Both X and Y
        Coordinates Which Will Make The Mouse Overshoot Beyond The Set Coordinates and Back. Max is 100%
        :param probability_of_overshoot: Probability The Mouse Will Overshoot. 0 - Will Never Happen, 1 - Will Always Happen
        :param is_small_distance: Advisable To Set To True If To MoveTo From Mouse Original Position Is Not Far Apart
        :param move_to_new_thread: Move Operations To Another Thread, If True
        :return: True When Done
        """
        screen_size = pyautogui.size()
        if x_coordinates >= screen_size[0]:
            x_coordinates = screen_size[0] - 2
        if y_coordinates >= screen_size[1]:
            y_coordinates = screen_size[1] - 2

        def move_operations():
            x_coordinates_to_move_to, y_coordinates_to_move_to = x_coordinates, y_coordinates

            # If Offset Percentages Are Set and Area Width And Height is Given
            if x_coordinates_offset_percentage > 0 and y_coordinates_offset_percentage > 0:
                # Calculate Offsets Based On Percentages
                x_coordinates_to_move_to = x_coordinates_to_move_to + utils.fetch_value_percentage(
                    x_coordinates_to_move_to, x_coordinates_offset_percentage)
                y_coordinates_to_move_to = y_coordinates_to_move_to + utils.fetch_value_percentage(
                    y_coordinates_to_move_to, y_coordinates_offset_percentage)

            self.human_clicker = HumanClicker()
            human_curve = None
            duration = random.uniform(0.2, 1.2)
            if is_small_distance:
                x_coordinates_to_move_to = int(x_coordinates_to_move_to)
                y_coordinates_to_move_to = int(y_coordinates_to_move_to)

                human_curve = HumanCurve(pyautogui.position(), (x_coordinates_to_move_to, y_coordinates_to_move_to),
                                         targetPoints=50)
                human_curve.points = human_curve.generateCurve(offsetBoundaryX=0, offsetBoundaryY=0,
                                                               leftBoundary=x_coordinates_to_move_to,
                                                               rightBoundary=x_coordinates_to_move_to + 1,
                                                               downBoundary=y_coordinates_to_move_to,
                                                               upBoundary=y_coordinates_to_move_to + 1,
                                                               knotsCount=5,
                                                               distortionMean=0, distortionStdev=0,
                                                               distortionFrequency=0,
                                                               tween=pytweening.linear,
                                                               targetPoints=50)
            if probability_of_overshoot > 0.5:
                self.human_clicker.move(
                    (int(x_coordinates_to_move_to + (x_coordinates_to_move_to *
                                                     random.randint(-max_overshoot, max_overshoot) / 100)),
                     int(y_coordinates_to_move_to + (y_coordinates_to_move_to *
                                                     random.randint(-max_overshoot, max_overshoot) / 100))),
                    humanCurve=human_curve,
                    duration=duration)

            self.human_clicker.move((int(x_coordinates_to_move_to), int(y_coordinates_to_move_to)),
                                    humanCurve=human_curve,
                                    duration=duration)

            print(f"Bot Process Id {self.bot_process_id} <:::> Mouse Moved To: ", x_coordinates_to_move_to,
                  y_coordinates_to_move_to)
            return {'x': int(x_coordinates_to_move_to), 'y': int(y_coordinates_to_move_to)}

        if move_to_new_thread:
            t = Thread(target=move_operations)
            t.daemon = True
            return t.start()
        else:
            return move_operations()

    def move_pointing_device_to_element(self, html_web_element: WebElement,
                                        simulate_human_behaviour=True):
        """
        :param html_web_element: HTML Element to Move To
        :param simulate_human_behaviour: If Bool is True(Which is By Default) use pyAutoGUI to Simulate Human Behaviour
        :return: return true on success
        """
        if simulate_human_behaviour:
            self.scroll_element_into_vertical_view(html_web_element, element_scroll_to=1)
            if not isinstance(self.touch, Touchscreen):
                element_screen_position = self.browser_interface.get_element_window_location_screen_offsets(html_web_element)
                el_pos = dict(area_x=element_screen_position["html_web_element"][0],
                              area_y=element_screen_position["html_web_element"][1],
                              area_width=html_web_element.rect["width"],
                              area_height=html_web_element.rect["height"])

                self.simulate_human_mouse_move_behavior_to_area(el_pos["area_x"] + 1, el_pos["area_y"] + 1,
                                                                el_pos["area_width"] - 2, el_pos["area_height"] - 2,
                                                                x_coordinates_offset_percentage=random.randint(0, 100),
                                                                y_coordinates_offset_percentage=random.randint(0, 100),
                                                                max_overshoot=35,
                                                                probability_of_overshoot=round(random.random(), 2))
        else:
            self.browser_interface.browser_action_chains.move_to_element_with_offset(html_web_element, 20, 20).perform()

    def scroll_to_percentage_in_element(self, html_web_element, percentage_to_scroll_to, time_to_sleep=1):
        def has_page_offset_changed():
            document_offsets = self.browser_interface.get_window_document_offsets()
            document_offsets = [document_offsets["x_offset"], document_offsets["y_offset"]]
            if self.last_document_offsets == document_offsets:
                return False
            else:
                return True

        def random_miscellaneous_key_presses(key_down_probability):
            for i in range(random.randint(1, 5)):
                if random.random() < key_down_probability:
                    self.keyboard.down(K_Keys["ArrowDown"])
                else:
                    self.keyboard.down(K_Keys["ArrowUp"])
                time.sleep(random.uniform(0.05, 0.45))

        def scroll_with_touch(direction, duration):
            if direction:
                px_to_adjust_by = random.randint(1, 500)
            if not direction:
                px_to_adjust_by = random.randint(-500, -1)
            self.read_with_touch(px_to_adjust_by, duration)

        def offset_adjuster(offset_to_adjust_to, html_web_element):
            element_coordinates = self.browser_interface.get_element_location_window_offset(html_web_element)
            if offset_to_adjust_to > element_coordinates["y_offset"]:
                if isinstance(self.touch, Touchscreen):
                    while offset_to_adjust_to >= element_coordinates["y_offset"]:
                        if not has_page_offset_changed():
                            return True
                        scroll_with_touch(False, 0.5)
                        element_coordinates = self.browser_interface.get_element_location_window_offset(html_web_element)
                else:
                    while offset_to_adjust_to >= element_coordinates["y_offset"]:
                        self.keyboard.down_persistent(K_Keys["ArrowUp"])
                        if utils.clean_negative(element_coordinates["y_offset"]) - utils.clean_negative(
                                offset_to_adjust_to) \
                                < bot_constants.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT:
                            time.sleep(random.uniform(0.01, 0.267))
                            self.keyboard.up(K_Keys["ArrowUp"])
                            time.sleep(random.uniform(0.15, 0.6))
                        else:
                            time.sleep(0.3)
                        element_coordinates = self.browser_interface.get_element_location_window_offset(html_web_element)
                    self.keyboard.up(K_Keys["ArrowUp"])
                    if random.random() > 0.5:
                        random_miscellaneous_key_presses(0.75)
            elif offset_to_adjust_to < element_coordinates["y_offset"]:
                if isinstance(self.touch, Touchscreen):
                    while offset_to_adjust_to <= element_coordinates["y_offset"]:
                        if not has_page_offset_changed():
                            return True
                        scroll_with_touch(True, 0.5)
                        element_coordinates = self.browser_interface.get_element_location_window_offset(html_web_element)
                else:
                    while offset_to_adjust_to <= element_coordinates["y_offset"]:
                        self.keyboard.down_persistent(K_Keys["ArrowDown"])
                        if utils.clean_negative(offset_to_adjust_to) - utils.clean_negative(
                                element_coordinates["y_offset"]) \
                                < bot_constants.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT:
                            time.sleep(random.uniform(0.01, 0.267))
                            self.keyboard.up(K_Keys["ArrowDown"])
                            time.sleep(random.uniform(0.15, 0.6))
                        else:
                            time.sleep(0.3)
                        element_coordinates = self.browser_interface.get_element_location_window_offset(html_web_element)
                    self.keyboard.up(K_Keys["ArrowDown"])
                    if random.random() > 0.5:
                        random_miscellaneous_key_presses(0.25)

        # Element Height - Browser Window Makes It Possible To Eject Browser Dimensions From Calculations
        workable_height = html_web_element.rect.get(
            "height") - self.browser_interface.web_browser_driver.get_window_rect().get("height")

        offset_to_adjust_to = utils.fetch_percentage_value(workable_height, percentage_to_scroll_to)
        offset_to_adjust_to *= -1

        original_y_offset = self.browser_interface.get_element_location_window_offset(html_web_element)["y_offset"]

        offset_adjuster(offset_to_adjust_to, html_web_element)
        time.sleep(time_to_sleep)
        offset_adjuster(original_y_offset, html_web_element)

    def read_with_arrow_keys(self, html_web_element, boundary, key=K_Keys["ArrowDown"], direction_to_move=True):
        self.keyboard.down_persistent(key)
        element_coordinates = self.browser_interface.get_element_location_window_offset(html_web_element)
        old_element_coordinates = element_coordinates
        boundary = element_coordinates.get("y_offset") - boundary
        offset_same_count = 0

        if direction_to_move:
            while element_coordinates.get("y_offset") >= boundary:
                old_element_coordinates = self.browser_interface.get_element_location_window_offset(html_web_element)
                time.sleep(0.1)
                element_coordinates = self.browser_interface.get_element_location_window_offset(html_web_element)

                if offset_same_count > 1:
                    break
                if element_coordinates.get("y_offset") == old_element_coordinates.get("y_offset"):
                    offset_same_count += 1

        elif not direction_to_move:
            while boundary >= element_coordinates.get("y_offset"):
                old_element_coordinates = self.browser_interface.get_element_location_window_offset(html_web_element)
                time.sleep(0.1)
                element_coordinates = self.browser_interface.get_element_location_window_offset(html_web_element)

                if offset_same_count > 1:
                    break
                if element_coordinates.get("y_offset") == old_element_coordinates.get("y_offset"):
                    offset_same_count += 1
        self.keyboard.up(key)
        return True

    def read_with_mouse_to_scrollbar(self,
                                     coordinates_offset_overshoot=dict(x=0, y=0, x_offset_percentage=0,
                                                                       y_offset_percentage=0, max_overshoot=0,
                                                                       probability_of_overshoot=0),
                                     is_asychronous=False, counter=0):
        pyautogui.mouseDown()
        if isinstance(self.smart_ads_interactions, SmartAdsInteractions) and self.smart_ads_interactions.no_of_clicks > 0:
            while self.browser_interface.revert_to_main_page():
                pyautogui.mouseUp()
                pyautogui.mouseDown()

        self.simulate_human_mouse_move_behavior_to_point(
            coordinates_offset_overshoot['x'], coordinates_offset_overshoot['y'],
            coordinates_offset_overshoot['x_offset_percentage'], coordinates_offset_overshoot['y_offset_percentage'],
            coordinates_offset_overshoot['max_overshoot'], coordinates_offset_overshoot['probability_of_overshoot'],
            True, is_asychronous)
        pyautogui.mouseUp()
        return counter

    def read_with_touch(self, px_to_adjust_by, duration=random.uniform(0.1, 2), force_screen_reset=False):
        # A List Containing The Browser's Page 9-Ways Splitted Dimension In The Following Format
        # [[(x, y, width, height) x3] x3]
        generated_page_boundaries = []
        if not hasattr(self, "generated_page_boundaries") or force_screen_reset:
            a_third_width = self.browser_interface.screen_width / 3
            a_third_height = self.browser_interface.screen_height / 3
            for h in range(3):
                generated_page_boundaries.append([])
                for w in range(3):
                    h_multiplier = h + 1
                    w_multiplier = w + 1
                    generated_page_boundaries[h].append(
                        (a_third_width * w, a_third_height * h,
                         a_third_width * w_multiplier, a_third_height * h_multiplier))
            self.generated_page_boundaries = generated_page_boundaries
        else:
            generated_page_boundaries = self.generated_page_boundaries

        if random.uniform(0.0, 1.0) <= 0.95:
            y_start = random.randint(round(generated_page_boundaries[2][1][1]),
                                     round(generated_page_boundaries[2][1][3]))
        else:
            if random.random() == 0:
                y_start = random.randint(round(generated_page_boundaries[0][1][1]),
                                         round(generated_page_boundaries[0][1][3]))
            else:
                y_start = random.randint(round(generated_page_boundaries[1][1][1]),
                                         round(generated_page_boundaries[1][1][3]))

        if random.uniform(0.0, 1.0) <= 0.95:
            x_start = random.randint(round(generated_page_boundaries[2][1][0]),
                                     round(generated_page_boundaries[2][1][2]))
        else:
            if random.random() == 0:
                x_start = random.randint(round(generated_page_boundaries[2][0][0]),
                                         round(generated_page_boundaries[2][0][2]))
            else:
                x_start = random.randint(round(generated_page_boundaries[2][2][0]),
                                         round(generated_page_boundaries[2][2][2]))
        y_end = round(y_start - px_to_adjust_by)
        x_end = round(x_start + utils.fetch_percentage_value(x_start, random.uniform(-4, 4)))

        x_start = x_start if x_start >= 0 else 0
        y_start = y_start if y_start >= 0 else 0
        x_end = x_end if x_end >= 0 else 0
        y_end = y_end if y_end >= 0 else 0

        self.touch.simulate_human_touch_movement_with_mouse((x_start, y_start), (x_end, y_end), duration)
        if isinstance(self.smart_ads_interactions, SmartAdsInteractions):
            self.smart_ads_interactions.smart_click_trigger((x_start, y_start), self.browser_interface.device_type)
            self.browser_interface.revert_to_main_page()

    def scroll_element_into_vertical_view(self, html_web_element: WebElement, element_scroll_to=1,
                                          simulate_human_behaviour=True):
        """
        This Method Scrolls The Web Page To Put Requested Web Element In View
        :param html_web_element: HTML Web Element To Scroll To
        :param element_scroll_to: Scroll To Top Or Bottom Of Element 1: 0 For Top, 1 For Bottom
        :param simulate_human_behaviour: If Argument Is True, Method Will Attempt To Simulate Human Interaction Scroll
        :return: Return True When Scroll Is Complete
        """

        def has_page_offset_changed():
            document_offsets = self.browser_interface.get_window_document_offsets()
            document_offsets = [document_offsets["x_offset"], document_offsets["y_offset"]]
            if self.last_document_offsets == document_offsets:
                return False
            else:
                return True

        def scroll(key):
            """
            Use Directional Keys To Scroll To Element
            :return: True
            """
            self.keyboard.down_persistent(key)
            time.sleep(random.uniform(1.1, 1.75))
            self.keyboard.up(key)
            time.sleep(random.uniform(0.5, 1.5))

        def scroll_with_touch(direction, duration):
            if direction:
                px_to_adjust_by = random.randint(1, 500)
            if not direction:
                px_to_adjust_by = random.randint(-500, -1)
            self.read_with_touch(px_to_adjust_by, duration)

        element_browser_coordinates = \
            self.browser_interface.get_element_window_location_screen_offsets(html_web_element)

        if simulate_human_behaviour:
            if element_scroll_to == 0:
                if element_browser_coordinates["html_web_element"][1] > \
                        element_browser_coordinates["browser_window_rect"][1]:
                    while element_browser_coordinates["html_web_element"][1] >= \
                            element_browser_coordinates["browser_window_rect"][1]:
                        if isinstance(self.touch, Touchscreen):
                            scroll_with_touch(True, 1)
                        else:
                            scroll(K_Keys["ArrowDown"])
                        if not has_page_offset_changed():
                            return True
                        element_browser_coordinates = self.browser_interface.get_element_window_location_screen_offsets(html_web_element)
                elif element_browser_coordinates["html_web_element"][1] < \
                        element_browser_coordinates["browser_window_rect"][1]:
                    while element_browser_coordinates["html_web_element"][1] <= \
                            element_browser_coordinates["browser_window_rect"][1]:
                        if isinstance(self.touch, Touchscreen):
                            scroll_with_touch(False, 1)
                        else:
                            scroll(K_Keys["ArrowUp"])
                        if not has_page_offset_changed():
                            return True
                        element_browser_coordinates = self.browser_interface.get_element_window_location_screen_offsets(html_web_element)

            elif element_scroll_to == 1:
                if element_browser_coordinates["html_web_element"][2] > \
                        element_browser_coordinates["browser_window_rect"][2]:
                    while element_browser_coordinates["html_web_element"][2] >= \
                            element_browser_coordinates["browser_window_rect"][2]:
                        if isinstance(self.touch, Touchscreen):
                            scroll_with_touch(True, 1)
                        else:
                            scroll(K_Keys["ArrowDown"])
                        if not has_page_offset_changed():
                            return True
                        element_browser_coordinates = self.browser_interface.get_element_window_location_screen_offsets(html_web_element)
                elif element_browser_coordinates["html_web_element"][1] < \
                        element_browser_coordinates["browser_window_rect"][1]:
                    while element_browser_coordinates["html_web_element"][1] <= \
                            element_browser_coordinates["browser_window_rect"][1]:
                        if isinstance(self.touch, Touchscreen):
                            scroll_with_touch(False, 1)
                        else:
                            scroll(K_Keys["ArrowUp"])
                        if not has_page_offset_changed():
                            return True
                        element_browser_coordinates = self.browser_interface.get_element_window_location_screen_offsets(html_web_element)

        else:
            self.browser_interface.browser_action_chains.move_to_element(html_web_element)

    def send_mouse_to_scrollbar(self, is_asychronous=False):
        scroll_bar = self.browser_interface.get_scroll_bar_coordinates(2)
        return self.simulate_human_mouse_move_behavior_to_area(
            scroll_bar['x_pos'] + 2, scroll_bar['y_pos'] + 2, scroll_bar['width'], scroll_bar['height'],
            random.randint(0, 100),
            random.randint(0, 100), 30, random.uniform(0.4, 1.0),
            is_asychronous)
