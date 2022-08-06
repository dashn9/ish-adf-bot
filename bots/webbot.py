# With Great Power Comes Great Responsibility

# Standard Library Imports
import os
import re
import sys
import pytweening
import random as rand
from threading import Thread

# External Python Packages
import time

import seleniumwire.undetected_chromedriver as sw_uc
from seleniumwire import webdriver, request
from seleniumwire.utils import decode
from seleniumwire.thirdparty.mitmproxy.net.http import encoding
from selenium.webdriver.remote import webdriver as remote_webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import pyautogui

from pyclick import HumanClicker, HumanCurve

# Internal Modules
from bots import utils
from constants import browser_constants, bot_constants
from constants.keyboard_keys import Keys as K_Keys
from bots.devtools.devtools_input import Keyboard, Touchscreen
from bots.devtools import devtools_mobile


class WebBot:  # A powerful WebBot designed to visit and perform activities on given url/s
    def __init__(
            self, url,
            browser_to_use_id=browser_constants.CHROME_ID,
            driver_path="/home/kali/PycharmProjects/ish_bots/SeleniumWebDrivers/Chrome/",
            ):
        """
        :param url: List of urls as List or a Single url String To Visit
        :param browser_to_use_id: By Default Chrome is Selected To Generate Randomly, use browser_constants.RAND_BROWSER
        Attribute
        :param driver_path: Location of WebDrivers. To Be Appended To The OS PATH ENV.
        """
        # Setting passed arguments to object
        if isinstance(url, list) or (url is None):
            self.url = url
        else:
            raise TypeError("Url Has To Be a List or None")

        self.browser_to_use_id = browser_to_use_id
        self.driver_path = driver_path

        # Browser Variables
        self.web_browser_driver: remote_webdriver.WebDriver = None
        self.browser_action_chains: ActionChains = None
        self.keyboard = None
        self.touch: Touchscreen = None
        self.opened_browser_urls = dict()
        self.human_clicker = HumanClicker()

        # pyclick
        self.human_clicker = HumanClicker()

        os.environ['PATH'] += r":" + driver_path

    def click_on_element(self, html_web_element):
        if isinstance(list, html_web_element):
            for ht_el in html_web_element:
                ht_el.click()
        else:
            html_web_element.click()

    def simulate_human_mouse_move_behavior_to_area(
            self, x_coordinates, y_coordinates, area_x_coordinates=0, area_y_coordinates=0, area_width=0, area_height=0, 
            x_coordinates_offset_percentage=0, y_coordinates_offset_percentage=0, max_overshoot=0, 
            probability_of_overshoot=0, is_small_distance=False, move_to_new_thread=False):
        """
        A Method To Simulate Human Mouse Behaviour To Specific Element On Screen. Powered By Pyclick and PyAutoGUI.
        Pass 1st and 2nd Argument To Click On a Specific Area. Pass Only The Next Six To Click On a Point Within an Area
        :param x_coordinates: The X coordinates On Screen To Move The Mouse To.
        If Clickable Area Exists, Make Sure It's Within Boundaries
        :param y_coordinates: The Y coordinates On Screen To Move The Mouse To.
        If Clickable Area Exists, Make Sure It's Within Boundaries
        :param area_x_coordinates: The X Coordinates Of Element On Screen
        :param area_y_coordinates: The Y Coordinates Of Element On Screen
        :param area_width: The Surface Width of The Element You Want to Get To On Screen. If it's Not Just A Point.
        Max is 100%
        :param area_height: The Surface Height of The Element You Want to Get To On Screen. If it's Not Just A Point
        Max is 100%
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
        def move_operations():
            x_coordinates_to_move_to, y_coordinates_to_move_to = x_coordinates, y_coordinates

            # If Offset Percentages Are Set and Area Width And Height is Given
            if (x_coordinates_offset_percentage > 0 and y_coordinates_offset_percentage > 0 and
                    area_width > 1 and area_height > 1):
                # Calculate Offsets Based On Percentages
                x_coordinates_to_move_to = (area_width * x_coordinates_offset_percentage / 100) + area_x_coordinates
                y_coordinates_to_move_to = (area_height * y_coordinates_offset_percentage / 100) + area_y_coordinates

                # If x_coordinates To Click On, Extends Beyond Width Bounds, Set To Bounds Point
                if x_coordinates_to_move_to < area_x_coordinates or x_coordinates_to_move_to > area_x_coordinates + area_width:
                    x_coordinates_to_move_to = area_x_coordinates

                # If y_coordinates To Click On, Extends Beyond Height Bounds, Set To Bounds Point
                if y_coordinates_to_move_to < area_y_coordinates or y_coordinates_to_move_to > area_y_coordinates + area_height:
                    y_coordinates_to_move_to = area_y_coordinates

            print("To Move To: ", x_coordinates_to_move_to, y_coordinates_to_move_to, probability_of_overshoot)
            self.human_clicker = HumanClicker()

            human_curve = None
            if is_small_distance:
                x_coordinates_to_move_to = int(x_coordinates_to_move_to)
                y_coordinates_to_move_to = int(y_coordinates_to_move_to)
                human_curve = HumanCurve(pyautogui.position(), (x_coordinates_to_move_to, y_coordinates_to_move_to))
                human_curve.points = human_curve.generateCurve(offsetBoundaryX=0, offsetBoundaryY=0, \
                                                               leftBoundary=x_coordinates_to_move_to,
                                                               rightBoundary=x_coordinates_to_move_to + 1, \
                                                               downBoundary=y_coordinates_to_move_to,
                                                               upBoundary=y_coordinates_to_move_to + 1, \
                                                               knotsCount=5, \
                                                               distortionMean=0.4, distortionStdev=0.2,
                                                               distortionFrequency=0.2, \
                                                               tween=pytweening.linear, \
                                                               targetPoints=50)
            if probability_of_overshoot > 0.5:

                self.human_clicker.move((int(x_coordinates_to_move_to + (
                            x_coordinates_to_move_to * rand.randint(-max_overshoot, max_overshoot) / 100)),
                         int(y_coordinates_to_move_to + (
                                     y_coordinates_to_move_to * rand.randint(-max_overshoot, max_overshoot) / 100))),
                        humanCurve = human_curve, duration = rand.uniform(0, 2))
            self.human_clicker.move((int(x_coordinates_to_move_to), int(y_coordinates_to_move_to)),
                                    humanCurve = human_curve, duration = rand.uniform(0, 2))
            return {'x': int(x_coordinates_to_move_to), 'y': int(y_coordinates_to_move_to)}

        if move_to_new_thread:
            return Thread(target=move_operations).start()
        else:
            return move_operations()

    def simulate_human_mouse_move_behavior_to_point(
            self, x_coordinates, y_coordinates, x_coordinates_offset_percentage=0, y_coordinates_offset_percentage=0,
            max_overshoot=0, probability_of_overshoot=0, is_small_distance=False, move_to_new_thread=False):
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
        :param is_small_distance: Advisable To Set To True If ToMoveTo From Mouse Original Position Is Not Far Apart
        :param move_to_new_thread: Move Operations To Another Thread, If True
        :return: True When Done
        """

        def move_operations():
            x_coordinates_to_move_to, y_coordinates_to_move_to = x_coordinates, y_coordinates

            # If Offset Percentages Are Set and Area Width And Height is Given
            if (x_coordinates_offset_percentage > 0 and y_coordinates_offset_percentage > 0 ):
                # Calculate Offsets Based On Percentages
                x_coordinates_to_move_to = x_coordinates_to_move_to + utils.fetch_value_percentage(
                    x_coordinates_to_move_to, x_coordinates_offset_percentage)
                y_coordinates_to_move_to = y_coordinates_to_move_to + utils.fetch_value_percentage(
                    y_coordinates_to_move_to, y_coordinates_offset_percentage)

            self.human_clicker = HumanClicker()
            human_curve = None
            if is_small_distance:
                x_coordinates_to_move_to = int(x_coordinates_to_move_to)
                y_coordinates_to_move_to = int(y_coordinates_to_move_to)
                
                human_curve = HumanCurve(pyautogui.position(), (x_coordinates_to_move_to, y_coordinates_to_move_to))
                human_curve.points = human_curve.generateCurve(offsetBoundaryX=0, offsetBoundaryY=0, \
                                  leftBoundary=x_coordinates_to_move_to, rightBoundary=x_coordinates_to_move_to+1, \
                                  downBoundary=y_coordinates_to_move_to, upBoundary=y_coordinates_to_move_to + 1, \
                                  knotsCount=5, \
                                  distortionMean=0, distortionStdev=0, distortionFrequency=0, \
                                  tween=pytweening.linear, \
                                  targetPoints=50)
            if probability_of_overshoot > 0.5:
                self.human_clicker.move(
                    (int(x_coordinates_to_move_to + (x_coordinates_to_move_to *
                                                     rand.randint(-max_overshoot, max_overshoot) / 100)),
                     int(y_coordinates_to_move_to + (y_coordinates_to_move_to *
                                                     rand.randint(-max_overshoot, max_overshoot) / 100))), humanCurve=human_curve,
                     duration=rand.uniform(0, 2))
            self.human_clicker.move((int(x_coordinates_to_move_to), int(y_coordinates_to_move_to)), humanCurve=human_curve,
                                    duration=rand.uniform(0, 2))
            return {'x': int(x_coordinates_to_move_to), 'y': int(y_coordinates_to_move_to)}

        if move_to_new_thread:
            return Thread(target=move_operations).start()
        else:
            return move_operations()

    def get_scroll_bar_coordinates(self, relative_to=0):
        """
        Calculates And Returns The Prospective Location And Dimesion Of The Browser Scrollbar
        :param relative_to: To Determine The Boundaries By Which To Calculate The Positions
        :return: The Position And Dimensions Of The ScrollBar In A Dictionary, False If No Scroll Bar Exists
        """
        browser_window_body_size = dict(
            width=self.web_browser_driver.execute_script("return document.body.getBoundingClientRect().width"),
            height=self.web_browser_driver.execute_script("return document.body.getBoundingClientRect().height"))

        browser_inner_size = dict(width=self.web_browser_driver.execute_script("return window.innerWidth"),
                                  height=self.web_browser_driver.execute_script("return window.innerHeight"))

        if browser_window_body_size.get("height") <= browser_inner_size.get("height"):
            # No Scrollbar
            return False

        # Fetch Browser Document Inner Offset
        window_page_y_offset = self.web_browser_driver.execute_script("return window.pageYOffset")
        window_page_y_offset = 1 if window_page_y_offset <= 0 else window_page_y_offset

        browser_outer_size = dict(width=self.web_browser_driver.execute_script("return window.outerWidth"),
                                  height=self.web_browser_driver.execute_script("return window.outerHeight"))

        scroll_bar_x_position = browser_window_body_size.get("width")
        scroll_bar_y_position = utils.fetch_percentage_value(
            browser_inner_size.get("height"),
            utils.fetch_value_percentage(browser_window_body_size.get("height"), window_page_y_offset))

        scroll_bar_width = browser_inner_size.get("width") - browser_window_body_size.get("width")

        scroll_bar_width = scroll_bar_width - 5 if scroll_bar_width > 0 else 10

        scroll_bar_height = utils.fetch_percentage_value(
            browser_inner_size.get("height"),
            utils.fetch_value_percentage(browser_window_body_size.get("height"), browser_inner_size.get("height")))

        scroll_bar_height = scroll_bar_height if scroll_bar_height > 0 else 15

        # Bound To Screen
        if relative_to == 2:
            browser_rect = self.web_browser_driver.get_window_rect()
            return {
                "x_pos": scroll_bar_x_position + browser_rect.get("x") +
                         (browser_outer_size.get("width") - browser_inner_size.get("width")),
                "y_pos": scroll_bar_y_position + browser_rect.get("y") +
                         (browser_outer_size.get("height") - browser_inner_size.get("height")),
                "width": scroll_bar_width,
                "height": scroll_bar_height
            }
        # Bound To Browser Window
        elif relative_to == 1:
            browser_rect = self.web_browser_driver.get_window_rect()
            return {
                "x_pos": scroll_bar_x_position + (browser_outer_size.get("width") - browser_inner_size.get("width")),
                "y_pos": scroll_bar_y_position + (browser_outer_size.get("height") - browser_inner_size.get("height")),
                "width": scroll_bar_width,
                "height": scroll_bar_height
            }
        # Bound To Web Page Inner Body
        elif relative_to == 0:
            return {
                "x_pos": scroll_bar_x_position,
                "y_pos": scroll_bar_y_position,
                "width": scroll_bar_width,
                "height": scroll_bar_height
            }
        else:
            return False

    def get_element_window_location_screen_offsets(self, html_web_element: remote_webdriver.WebElement):
        """
        Calculate And Return Both Window And Element Location Offsets Relative To Screen
        :param html_web_element: Target HTML Element
        :return: Offset Locations Of Element(tuple) And Browser(tuple) In a Dict()
        """
        # Getting HTML Web Element Coordinates Which Are Relative From The Window Point) And Dimensions
        web_element_location_dimensions = html_web_element.rect

        # Fetch Browser Document Inner Offset
        window_page_y_offset = self.web_browser_driver.execute_script("return window.pageYOffset")
        window_page_x_offset = self.web_browser_driver.execute_script("return window.pageXOffset")

        browser_inner_size = dict(width=self.web_browser_driver.execute_script("return window.innerWidth"),
                                  height=self.web_browser_driver.execute_script("return window.innerHeight"))
        browser_window_rect = self.web_browser_driver.get_window_rect()
        web_element_x_offset = web_element_location_dimensions.get("x") + browser_window_rect.get("x") \
                               + (browser_window_rect.get("width") - browser_inner_size["width"]) \
                               - window_page_x_offset
        web_element_y_offset = web_element_location_dimensions.get("y") + browser_window_rect.get("y") \
                               + (browser_window_rect.get("height") - browser_inner_size["height"]) \
                               - window_page_y_offset
        browser_window_rect_bottom = browser_window_rect.get("height") + browser_window_rect.get("y")
        web_element_bottom = web_element_y_offset + web_element_location_dimensions.get(
            "height")
        return {"html_web_element": (web_element_x_offset, web_element_y_offset, web_element_bottom),
                "browser_window_rect": (
                browser_window_rect.get("x"), browser_window_rect.get("y"), browser_window_rect_bottom)}

    def get_element_location_window_offset(self, html_web_element: remote_webdriver.WebElement):
        """
        Calculate And Return Both Element Location Offsets Relative To Window
        :param html_web_element: Target HTML Element
        :param browser_window_rect: Target Web Browser Window Panel Size And Coordinates
        :return: Offset Locations Of Element(tuple) And Browser(tuple) In a Dict()
        """
        # Getting HTML Web Element Coordinates Which Are Relative From The Window Point) And Dimensions
        web_element_location_dimensions = html_web_element.rect

        # Fetch Browser Document Inner Offset
        window_page_y_offset = self.web_browser_driver.execute_script("return window.pageYOffset")
        window_page_x_offset = self.web_browser_driver.execute_script("return window.pageXOffset")

        web_element_x_offset = web_element_location_dimensions.get("x") - window_page_x_offset
        web_element_y_offset = web_element_location_dimensions.get("y") - window_page_y_offset

        web_element_bottom = web_element_y_offset + web_element_location_dimensions.get(
            "height")
        return {"x_offset": web_element_x_offset, "y_offset": web_element_y_offset, "bottom": web_element_bottom}

    def scroll_element_into_vertical_view(self, html_web_element: remote_webdriver.WebElement, browser_window_rect,
                                          browser_inner_size: dict, action_chains: ActionChains,
                                          element_scroll_to=1, simulate_human_behaviour=True):
        """
                    This Method Scrolls The Web Page To Put Requested Web Element In View
                    :param html_web_element: HTML Web Element To Scroll To
                    :param browser_window_rect: Browser Windows Screen Location and Screen Size
                    :param browser_inner_size: Browser Window Inner Size For Web Page Panel
                    :param action_chains: Action Chains of The Browser Driver
                    :param element_scroll_to: Scroll To Top Or Bottom Of Element 1: 0 For Top, 1 For Bottom
                    :param simulate_human_behaviour: If Argument Is True, Method Will Attempt To Simulate Human Interaction Scroll
                    :return: Return True When Scroll Is Complete
                    """

        def use_directional_keys_to_navigate(direction_to_move, html_web_element: remote_webdriver.WebElement,
                                             element_scroll_to=1):
            """
            Use Directional Keys To Scroll To Element
            :return: True
            """
            element_browser_coordinates = \
                self.get_element_window_location_screen_offsets(html_web_element)
            coordinates_index = 2
            if element_scroll_to == 0:
                coordinates_index = 1

            while element_browser_coordinates["html_web_element"][coordinates_index] >= \
                    element_browser_coordinates["browser_window_rect"][coordinates_index]:
                self.keyboard.down_persistent(direction_to_move)
                time.sleep(rand.uniform(0.1, 1.45))
                self.keyboard.up(direction_to_move)
                time.sleep(rand.uniform(1.0, 3.0))
                element_browser_coordinates = \
                    self.get_element_window_location_screen_offsets(html_web_element)
                # print(element_browser_coordinates)
                pass
        if simulate_human_behaviour:
            use_directional_keys_to_navigate(K_Keys["ArrowDown"], html_web_element, 0)
        else:
            action_chains.move_to_element(html_web_element)

    def looper(self, read_time, direction_to_move, html_web_element, total_px_to_adjust_by,
               rem_px_to_adjust_by, rem_read_time, owing_misc_time, mode="arrow_keys", **kwargs):
        element_coordinates = self.get_element_location_window_offset(html_web_element)
        browser_inner_size = browser_inner_size=dict(width=self.web_browser_driver.execute_script("return window.innerWidth"),
                                    height=self.web_browser_driver.execute_script("return window.innerHeight"))
        if rand.randint(0, 1):
            px_to_adjust_by = rand.randint(1, round(browser_inner_size.get("height") / 1.5))
        else:
            px_to_adjust_by = rand.randint(1, round(self.web_browser_driver.get_window_rect().get("height") / 2))
        print("Original Px To adjust by: ", px_to_adjust_by)
        element_base_offset = element_coordinates.get("y_offset")
        print(element_coordinates)
        # Update Misc Time
        misc_time = time.time()

        def send_mouse_to_scrollbar(is_asychronous=False):
            scroll_bar = self.get_scroll_bar_coordinates(2)
            return self.simulate_human_mouse_move_behavior_to_area(
                scroll_bar['x_pos'] - 2, scroll_bar['y_pos'] + 10, scroll_bar['x_pos'] - 2, scroll_bar['y_pos'] + 10,
                scroll_bar['width'],
                scroll_bar['height'], rand.randint(0, 100), rand.randint(0, 100), 30, rand.uniform(0.4, 1.0), is_asychronous)

        def read_with_arrow_keys(element_coordinates, boundary, key=K_Keys["ArrowDown"], direction_to_move=True):
            self.keyboard.down_persistent(key)
            if direction_to_move:
                while element_coordinates.get("y_offset") >= boundary:
                    time.sleep(0.1)
                    element_coordinates = self.get_element_location_window_offset(html_web_element)

            elif not direction_to_move:
                while element_coordinates.get("y_offset") >= boundary:
                    time.sleep(0.1)
                    element_coordinates = self.get_element_location_window_offset(html_web_element)
            self.keyboard.up(direction_to_move)
            return True

        def read_with_mouse_to_scrollbar(
                coordinates_offset_overshoot={'x': 0, 'y': 0, 'x_offset_percentage': 0, 'y_offset_percentage': 0,
                'max_overshoot': 0, 'probability_of_overshoot': 0}, is_asychronous=False, counter=0):
            pyautogui.mouseDown()
            self.simulate_human_mouse_move_behavior_to_point(
                coordinates_offset_overshoot['x'], coordinates_offset_overshoot['y'],
                coordinates_offset_overshoot['x_offset_percentage'], coordinates_offset_overshoot['y_offset_percentage'],
                coordinates_offset_overshoot['max_overshoot'], coordinates_offset_overshoot['probability_of_overshoot'],
                True, is_asychronous)
            return counter

        def read_with_touch(px_to_adjust_by, duration, force_screen_reset=False):
            #A List Containing The Browser's Page 9-Ways Splitted Dimension In The Following Format
            #[[(x, y, width, height) x3] x3]
            generated_page_boundaries = []
            if not hasattr(self, "generated_page_boundaries") or force_screen_reset:
                browser_inner_size = dict(width=self.web_browser_driver.execute_script("return window.innerWidth"),
                                          height=self.web_browser_driver.execute_script("return window.innerHeight"))
                a_third_width = browser_inner_size["width"] / 3
                a_third_height = 700 / 3
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

            if rand.uniform(0.0, 1.0) <= 0.95:
                y_start = rand.randint(round(generated_page_boundaries[2][1][1]),
                                       round(generated_page_boundaries[2][1][3]))
            else:
                if rand.random() == 0:
                    y_start = rand.randint(round(generated_page_boundaries[0][1][1]),
                                           round(generated_page_boundaries[0][1][3]))
                else:
                    y_start = rand.randint(round(generated_page_boundaries[1][1][1]),
                                           round(generated_page_boundaries[1][1][3]))

            if rand.uniform(0.0, 1.0) <= 0.95:
                x_start = rand.randint(round(generated_page_boundaries[2][1][0]),
                                       round(generated_page_boundaries[2][1][2]))
            else:
                if rand.random() == 0:
                    x_start = rand.randint(round(generated_page_boundaries[2][0][0]),
                                           round(generated_page_boundaries[2][0][2]))
                else:
                    x_start = rand.randint(round(generated_page_boundaries[2][2][0]),
                                           round(generated_page_boundaries[2][2][2]))
            y_end = round(y_start - px_to_adjust_by)
            x_end = round(x_start + utils.fetch_percentage_value(x_start, rand.uniform(-4, 4)))

            x_start = x_start if x_start >= 0 else 0
            y_start = y_start if y_start >= 0 else 0
            x_end = x_end if x_end >= 0 else 0
            y_end = y_end if y_end >= 0 else 0

            if not duration:
                duration = rand.uniform(0.1, 3)
            self.touch.simulate_human_touch_movement_with_mouse((x_start, y_start), (x_end, y_end), duration)
        if mode == "arrow_keys":
            pass
        elif mode == "touch":
            read_duration = 3
            if owing_misc_time >= 1:
                read_duration /= owing_misc_time
            read_with_touch(px_to_adjust_by, read_duration)
        elif mode == "mouse_to_scrollbar":
            if "present_mouse_points" in kwargs:
                mouse_x, mouse_y = pyautogui.position()
                mouse_x += utils.fetch_percentage_value(browser_inner_size["height"], rand.randint(-1, 1))
                mouse_y += ((px_to_adjust_by / self.web_browser_driver.execute_script(
                    "return document.body.getBoundingClientRect().height")) * browser_inner_size["height"])
                kwargs["present_mouse_points"]["x"] = mouse_x
                kwargs["present_mouse_points"]["y"] = mouse_y
                read_with_mouse_to_scrollbar(
                {'x': mouse_x, 'y': mouse_y, 'x_offset_percentage': 0,
                'y_offset_percentage': 0, 'max_overshoot': 0, 'probability_of_overshoot': 0})
            else:
                present_mouse_points = send_mouse_to_scrollbar()
                if not isinstance(present_mouse_points, dict):
                    raise TypeError("Set Function Asychronous Parameter To False, If Expecting Dict Of Mouse Coordinates")
                mouse_x, mouse_y = present_mouse_points.values()
                kwargs["present_mouse_points"] = present_mouse_points
                time.sleep(rand.uniform(0, 1))

        # Wait So Browser Can Fully Complete Scroll
        time.sleep(0.12)
        element_coordinates = self.get_element_location_window_offset(html_web_element)
        # Changing The Value Of px_to_adjust_by To The Amount Of px Actually Adjusted
        px_to_adjust_by = (element_base_offset - element_coordinates.get("y_offset"))

        if px_to_adjust_by > rem_px_to_adjust_by:
            px_to_adjust_by = rem_px_to_adjust_by
        else:
            rem_px_to_adjust_by -= px_to_adjust_by

        percentage_of_seconds_to_hang_for = utils.fetch_value_percentage(total_px_to_adjust_by, px_to_adjust_by)

        offset_percentage_of_seconds_to_hang_for = utils.fetch_percentage_value(
            percentage_of_seconds_to_hang_for, 15)
        offset_percentage_of_seconds_to_hang_for = rand.uniform(-offset_percentage_of_seconds_to_hang_for,
                                                                offset_percentage_of_seconds_to_hang_for)

        percentage_of_seconds_to_hang_for += offset_percentage_of_seconds_to_hang_for

        seconds_to_hang_for = utils.fetch_percentage_value(
            read_time, percentage_of_seconds_to_hang_for) - (time.time() - misc_time)

        # If Miscelleanous Time Is Greater Than Seconds To Hang For, Do This
        if seconds_to_hang_for - owing_misc_time < 0:
            owing_misc_time -= seconds_to_hang_for
            seconds_to_hang_for = 0
        else:
            # Restore Owing Misc Time If Deducted Debt Could Not Make Seconds To Hang For Lesser Than 0
            seconds_to_hang_for -= owing_misc_time
            owing_misc_time = 0

        rem_read_time -= seconds_to_hang_for
        print(read_time, rem_read_time, seconds_to_hang_for,
              px_to_adjust_by, time.time() - misc_time)

        time.sleep(round(seconds_to_hang_for, 2))
        print("Remaining PX To Adjust By ", rem_px_to_adjust_by)
        if rem_px_to_adjust_by > 0:
            self.looper(read_time, direction_to_move, html_web_element, total_px_to_adjust_by,
                        rem_px_to_adjust_by, rem_read_time, owing_misc_time, mode, **kwargs)
        else:
            return False

    def read_element_content(self, html_web_element: remote_webdriver.WebElement, browser_window_rect,
                             browser_inner_size: dict, action_chains: ActionChains):
        """
        This Method Scrolls The Web Page To Put Requested Web Element In View
        :param html_web_element: HTML Web Element To Scroll To
        :param browser_window_rect: Browser Windows Screen Location and Screen Size
        :param browser_inner_size: Browser Window Inner Size For Web Page Panel
        :param action_chains: Action Chains of The Browser Driver
        :return: Return True When Scroll Is Complete
        """
        def use_directional_keys_to_read(read_time, direction_to_move, html_web_element: remote_webdriver.WebElement,
                                         percentage_of_content_to_read=100):
            """
            Use Directional Keys To Scroll To Element
            :param read_time: Amount Of Time To Move Through Content
            :param direction_to_move: Arrow Keys To Use
            :param html_web_element: HTML Web Element To Scroll To
            :param percentage_of_content_to_read: Percentage Of Article Height To Stop At
            :return: True
            """
            # Get The Total Pixels To Move By Using The percentage_of_content_to_read On html_web_element Height
            total_px_to_adjust_by = utils.fetch_percentage_value(
                self.get_element_location_window_offset(html_web_element)["bottom"],
                percentage_of_content_to_read)
            rem_px_to_adjust_by = total_px_to_adjust_by
            rem_read_time = read_time
            owing_misc_time = 0
            self.looper(read_time, direction_to_move, html_web_element, total_px_to_adjust_by,
                        rem_px_to_adjust_by, rem_read_time, owing_misc_time, "touch")

            print("done")
        seconds_to_read = self.calculate_and_generate_page_read_time(html_web_element)
        content_read_percentage = rand.randint(85, 100)
        self.scroll_element_into_vertical_view(
            html_web_element, browser_window_rect=self.web_browser_driver.get_window_rect(),
            browser_inner_size=dict(width=self.web_browser_driver.execute_script("return window.innerWidth"),
                                    height=self.web_browser_driver.execute_script("return window.innerHeight")),
            element_scroll_to=0, action_chains=self.browser_action_chains
        )
        remaining_reading_time = seconds_to_read
        next_read_sequence_time = rand.randint(0, remaining_reading_time)

        # If Amount Of Seconds To Read For Next Is Less Than 8% Of Originally Assigned Time. Assign Remaining Reading Time To It
        if next_read_sequence_time < utils.fetch_percentage_value(seconds_to_read, 8):
            next_read_sequence_time = remaining_reading_time

        remaining_reading_content_percentage = content_read_percentage
        next_read_sequence_percentage = utils.fetch_percentage_value(
            content_read_percentage, utils.fetch_value_percentage(seconds_to_read, next_read_sequence_time)) \
            + rand.uniform(-2.2, 2.2)
        print(remaining_reading_content_percentage, remaining_reading_time)
        # while remaining_reading_content_percentage >= 0 and remaining_reading_time >= 0:
           # print("first_remaining")
        use_directional_keys_to_read(remaining_reading_time, K_Keys["ArrowDown"], html_web_element,
                                     100)

    def calculate_and_generate_page_read_time(self, html_web_element_to_read: remote_webdriver.WebElement = None,
                                              reading_speed=700, max_offset=20):
        """
        A Method To Calculate And Generate an Expected Read Time For Web Text Content Based On Set 'Words Scanning Per
        Minute(WSPM)' With Randomly Generated Offsets At a Max Which Can Be Either Positive or Negative
        :param html_web_element_to_read: Element Containing Web Text Content To Read On. If None, Method Tries To
        Fetch The Article Element Of The Web Page
        :param reading_speed: The Set Reading Speed Of Which Calculations Will Be Performed Upon. Average is 2100
        :param max_offset: The Maximum Percentage A Randomly Generated Offset Can Attain Either Positive or Negative
        :return: Returns Amount Of Seconds To Read Content For
        """
        if not html_web_element_to_read:
            html_web_element_to_read = self.web_browser_driver.find_element(By.TAG_NAME, "article")

        all_element_words = html_web_element_to_read.text.split()
        words_len = len(all_element_words)
        seconds_to_read = (words_len / reading_speed) * 60
        seconds_to_read += (seconds_to_read * rand.randint(-max_offset, max_offset) / 100)

        # Convert To Seconds And Return
        return round(seconds_to_read)

    def move_mouse_to_element(self, html_web_element: remote_webdriver.WebElement, simulate_human_behaviour):
        """
        :param html_web_element: HTML Element to Move To
        :param simulate_human_behaviour: If Bool is True(Which is By Default) use pyAutoGUI to Simulate Human Behaviour
        :return: return true on success
        """
        if simulate_human_behaviour:
            element_location_and_dimensions = dict(area_x_coordinates=62, area_y_coordinates=86,
                                                   area_width=182, area_height=52)

            self.simulate_human_mouse_move_behavior_to_area(62 + 91, 86 + 26, **element_location_and_dimensions,
                                         x_coordinates_offset_percentage=rand.randint(0, 100),
                                         y_coordinates_offset_percentage=rand.randint(0, 100), max_overshoot=35,
                                         probability_of_overshoot=round(rand.random(), 2))
        else:
            self.browser_action_chains.move_to_element_with_offset(html_web_element, 20, 20).perform()

    def inject_js_to_spoof_fingerprintable_objects_on_website_server_response(
            self, request: request.Request, response: request.Response):
        """
        A Method
        :param: The Orginal Request
        :param response: The Response of The Web Server To Adjust Before Reaching Browser
        :return: True On Success, False On Failure
        """
        if response:
            if ((response.headers.get('content-type').find('text/html') or
                    not re.search(r'(?<!https:)(?<!https:/)(\/\w)$', request.url) or re.match(r'(.html|.htm)$', request.url))
                    and request.method == 'GET' and response.status_code == 200):

                body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
                body = body.decode('utf-8')
                if body.find("<head>") != -1:
                    body = utils.insert_text_into_string(
                        body,
                        "<script>"+utils.return_fingerprintables_spoof_js_code(
                            offset_color_value=(-1, 0, 0, 0), audio_context_offset=0.8719691574200679)+"</script>",
                        "<head>", True)
                else:
                    body = utils.insert_text_into_string_reg(
                        body, "alert(\"i be gee\");\n console.log(\"I ran\");", r"(<script>)|(<script .*?>)", True)
                body = str.encode(body)
                response.body = encoding.encode(body, response.headers.get('Content-Encoding', 'identity'))
                del self.web_browser_driver.response_interceptor
                return True
        return False

    def open_web_browser(self, executable_path=bot_constants.WEB_DRIVERS_BASE_LOCATION
                            + bot_constants.WEB_DRIVERS_CHROME_LOCATION
                            + bot_constants.CHROME_WEBDRIVER,
                            chrome_binary_path=browser_constants.CHROME_BINARY_LOCATION):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = chrome_binary_path
        #chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #chrome_options.add_experimental_option('useAutomationExtension', False)
        #chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        #chrome_options.add_experimental_option("mobileEmulation", {"deviceName": "Google Nexus 7"})

        try:
            self.web_browser_driver = sw_uc.Chrome(driver_executable_path=executable_path, chrome_options=chrome_options)
            devtools_mobile.activate_mobile(
                self.web_browser_driver, {'width': 390, 'height': 844, 'deviceScaleFactor': 3, 'mobile': True}, 5)
            self.browser_action_chains = ActionChains(self.web_browser_driver)
            self.keyboard = Keyboard(self.web_browser_driver)
            self.touch = Touchscreen(self.web_browser_driver, self.keyboard)

        except IOError as io_error:
            print(io_error)
            print("Something Went Wrong During Browser Instantiation.\n"
                  "Make Sure Your ChromeDriver Is At The Right Location. Check The Web Browsers Constants.\n"
                  "Also Make Sure The Browser Executable Is At The Right Location")
            sys.exit(1)
        self.web_browser_driver.implicitly_wait(bot_constants.IMPLICITLY_WAIT_TIME)
        self.open_url_on_browser("https://www.gotchseo.com/blogspot/", "jk-finance.blogspot.com")

        self.read_element_content(self.web_browser_driver.find_element(By.TAG_NAME,
            "article"),
            browser_window_rect=self.web_browser_driver.get_window_rect(),
            browser_inner_size=dict(width=self.web_browser_driver.execute_script("return window.innerWidth"),
                                    height=self.web_browser_driver.execute_script("return window.innerHeight")),
            action_chains=self.browser_action_chains)
        time.sleep(400)

    def open_new_tab(self, url):
        """
        :param url: Url Location Of The WebPage
        :return: Return True On Success
        """
        try:
            self.web_browser_driver.execute_script(f"window.open();")
            self.web_browser_driver.switch_to.window(self.web_browser_driver.window_handles[-1])
            self.web_browser_driver.response_interceptor = \
                self.inject_js_to_spoof_fingerprintable_objects_on_website_server_response
            if url:
                self.web_browser_driver.get(url)
            return self.web_browser_driver.current_window_handle
        except (NameError, TypeError):
            return False

    def open_url_on_browser(self, url: str, url_name: str, force_browser_diversion=False):
        """
        :param url: The Url To Open, First Url Name To Be Opened Is Never Used
        :param url_name: Name Of The Url To Allow Easy Navigation On Browser
        :param force_browser_diversion: Bool Flag To Open Url On Another Opened Browser if Chrome is Not Alive
        :return: If False,  The URL Name is Present in Chrome, If True Then The Url Has Successfully Been Opened
        """
        if self.web_browser_driver:
            if url_name in self.opened_browser_urls:
                print(url_name + " is identifying a url already, use another url name or resolve code to select more unique name")
                return False
            else:
                if not self.opened_browser_urls:  # If first Url To Browser,
                    # Open New And Terminate First Because It Has No Name Identifier
                    self.opened_browser_urls[url_name] = self.web_browser_driver.window_handles[0]
                    self.web_browser_driver.response_interceptor = \
                        self.inject_js_to_spoof_fingerprintable_objects_on_website_server_response
                    self.web_browser_driver.get(url)
                else:
                    url_id = self.open_new_tab(url)
                    if url_id:
                        self.opened_browser_urls[url_name] = url_id
                        print(self.opened_browser_urls)
                    else:
                        print("Unable To Open Url: " + url + ", With Name: " + url_name)
                    return True
        elif force_browser_diversion:
            """Create A Method That Checks All Other Opened Browsers To 
        Open The Url Incase Chrome Isn't Alive"""
        else:
            raise NameError("No Available Chrome Browser, Either Set One Up by Using The "
                            "'open_web_browser_driver' or Force Browser Diversion")
        return False
    