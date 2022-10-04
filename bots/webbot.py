# With Great Power Comes Great Responsibility

# Standard Library Imports
import ctypes
import re
import pytweening
import random as rand
from threading import Thread
from multiprocessing import Value

# External Python Packages
import time

import seleniumwire.undetected_chromedriver as sw_uc
from seleniumwire import webdriver, request
from seleniumwire.utils import decode
from seleniumwire.thirdparty.mitmproxy.net.http import encoding
from selenium.webdriver.remote import webdriver as remote_webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import pyautogui

from pyclick import HumanClicker, HumanCurve

# Internal Modules
from bots import utils
from constants import browser_constants, bot_constants
from constants.keyboard_keys import Keys as K_Keys
from bots.devtools.devtools_input import Keyboard, Touchscreen, Mouse
from bots.devtools import devtools_primary
from identity.client import Identity


class WebBot:  # A powerful WebBot designed to visit and perform activities on given url/s
    active_on_mouse_movement = Value(ctypes.c_int, -1)
    def __init__(
            self, identity=None,
            browser_to_use_id=browser_constants.CHROME_ID,
            driver_path=f"{bot_constants.FULL_DIRECTORY_PATH}/SeleniumWebDrivers/Chrome/chromedriver",
            bot_process_id=None
    ):
        """
        :param url: List of urls as List or a Single url String To Visit
        :param browser_to_use_id: By Default Chrome is Selected To Generate Randomly, use browser_constants.RAND_BROWSER
        Attribute
        :param driver_path: Location of WebDrivers. To Be Appended To The OS PATH ENV.
        """
        self.time_activated = time.time()
        self.bot_process_id = bot_process_id
        if not identity:
            if browser_to_use_id == browser_constants.CHROME_ID:
                browser_name = "chrome"
            elif browser_to_use_id == browser_constants.FIREFOX_ID:
                browser_name = "firefox"
            else:
                browser_name = "chrome"
            self.identity = Identity(
                id=0, device_type="is_pc", hardware="Desktop", user_agent_os="Windows NT 10.0; Win64; x64",
                platform="Win32", canvas_fp_offset=[0, 0, 0, -1], audio_context_fp_offset=0.2, font_fp_offset=[1, 1],
                webgl_fp_offset=[0.9343, 0.3453], hardware_concurrency=4, memory=4, has_mouse="has_mouse",
                has_battery="no_battery", has_touch="no_touch", browser_name=browser_name, browser_version=None,
                screen_resolution=None, gpu_vendor="Google Inc. (Intel)", gpu_renderer="Intel(R) HD Graphics",
                vpn_client=None, ovpn_file_name=None, referer="https://l.facebook.com", reading_speed=900,
                timezone=["Etc/GMT", 0, "AM Coordinated Time"], mouse_delta_y=50)
        else:
            self.identity = identity
        self.browser_to_use_id = browser_to_use_id
        self.driver_path = driver_path

        pyautogui.FAILSAFE = False
        # Browser Variables
        self.web_browser_driver: remote_webdriver.WebDriver = None
        self.browser_action_chains: ActionChains = None
        self.keyboard = None
        self.touch: Touchscreen = None
        self.mouse = None
        self.opened_browser_urls = dict()
        self.human_clicker = HumanClicker()
        self.last_document_offsets = [0, 0]
        self.referer_use_times = 0

        # pyclick
        self.human_clicker = HumanClicker()

    def click_on_element(self, html_web_element):
        if isinstance(list, html_web_element):
            for ht_el in html_web_element:
                ht_el.click()
        else:
            html_web_element.click()

    def simulate_human_mouse_move_behavior_to_area(
            self, x_coordinates, y_coordinates, area_width=1, area_height=1,
            x_coordinates_offset_percentage=0, y_coordinates_offset_percentage=0, max_overshoot=0,
            probability_of_overshoot=0, is_small_distance=False, move_to_new_thread=False):
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
                x_coordinates_to_move_to = (area_width * x_coordinates_offset_percentage / 100) + x_coordinates_to_move_to
                y_coordinates_to_move_to = (area_height * y_coordinates_offset_percentage / 100) + y_coordinates_to_move_to

                # If x_coordinates To Click On, Extends Beyond Width Bounds, Set To Bounds Point
                if x_coordinates_to_move_to < x_coordinates or x_coordinates_to_move_to > x_coordinates + area_width:
                    x_coordinates_to_move_to = x_coordinates + (area_width / 2)

                # If y_coordinates To Click On, Extends Beyond Height Bounds, Set To Bounds Point
                if y_coordinates_to_move_to < y_coordinates or y_coordinates_to_move_to > y_coordinates + area_height:
                    y_coordinates_to_move_to = y_coordinates + (area_height / 2)

            self.human_clicker = HumanClicker()

            human_curve = None
            duration = rand.uniform(0.2, 2)
            if is_small_distance:
                x_coordinates_to_move_to = int(x_coordinates_to_move_to)
                y_coordinates_to_move_to = int(y_coordinates_to_move_to)
                human_curve = HumanCurve(pyautogui.position(), (x_coordinates_to_move_to, y_coordinates_to_move_to),
                                         targetPoints=50)
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
                                                 y_coordinates_to_move_to * rand.randint(-max_overshoot,
                                                                                         max_overshoot) / 100))),
                                        humanCurve=human_curve, duration=duration)
            self.human_clicker.move((int(x_coordinates_to_move_to), int(y_coordinates_to_move_to)),
                                    humanCurve=human_curve, duration=duration)

            print(f"Bot Process Id {self.bot_process_id} <:::> Mouse Moved To Area Point: ", x_coordinates_to_move_to, y_coordinates_to_move_to)
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
            if (x_coordinates_offset_percentage > 0 and y_coordinates_offset_percentage > 0):
                # Calculate Offsets Based On Percentages
                x_coordinates_to_move_to = x_coordinates_to_move_to + utils.fetch_value_percentage(
                    x_coordinates_to_move_to, x_coordinates_offset_percentage)
                y_coordinates_to_move_to = y_coordinates_to_move_to + utils.fetch_value_percentage(
                    y_coordinates_to_move_to, y_coordinates_offset_percentage)

            self.human_clicker = HumanClicker()
            human_curve = None
            duration = rand.uniform(0.2, 2)
            if is_small_distance:
                x_coordinates_to_move_to = int(x_coordinates_to_move_to)
                y_coordinates_to_move_to = int(y_coordinates_to_move_to)

                human_curve = HumanCurve(pyautogui.position(), (x_coordinates_to_move_to, y_coordinates_to_move_to),
                                         targetPoints=50)
                human_curve.points = human_curve.generateCurve(offsetBoundaryX=0, offsetBoundaryY=0, \
                                                               leftBoundary=x_coordinates_to_move_to,
                                                               rightBoundary=x_coordinates_to_move_to + 1, \
                                                               downBoundary=y_coordinates_to_move_to,
                                                               upBoundary=y_coordinates_to_move_to + 1, \
                                                               knotsCount=5, \
                                                               distortionMean=0, distortionStdev=0,
                                                               distortionFrequency=0, \
                                                               tween=pytweening.linear, \
                                                               targetPoints=50)
            if probability_of_overshoot > 0.5:
                self.human_clicker.move(
                    (int(x_coordinates_to_move_to + (x_coordinates_to_move_to *
                                                     rand.randint(-max_overshoot, max_overshoot) / 100)),
                     int(y_coordinates_to_move_to + (y_coordinates_to_move_to *
                                                     rand.randint(-max_overshoot, max_overshoot) / 100))),
                    humanCurve=human_curve,
                    duration=duration)

            self.human_clicker.move((int(x_coordinates_to_move_to), int(y_coordinates_to_move_to)),
                                    humanCurve=human_curve,
                                    duration=duration)

            print(f"Bot Process Id {self.bot_process_id} <:::> Mouse Moved To: ", x_coordinates_to_move_to, y_coordinates_to_move_to)
            return {'x': int(x_coordinates_to_move_to), 'y': int(y_coordinates_to_move_to)}

        if move_to_new_thread:
            return Thread(target=move_operations).start()
        else:
            return move_operations()

    def get_browser_window_body_size(self):
        return dict(width=self.web_browser_driver.execute_script("return document.body.getBoundingClientRect().width"),
                    height=self.web_browser_driver.execute_script(
                        "return document.body.getBoundingClientRect().height"))

    def get_browser_inner_size(self):
        return dict(width=self.web_browser_driver.execute_script("return window.innerWidth"),
                    height=self.web_browser_driver.execute_script("return window.innerHeight"))

    def get_scroll_bar_coordinates(self, relative_to=0):
        """
        Calculates And Returns The Prospective Location And Dimesion Of The Browser Scrollbar
        :param relative_to: To Determine The Boundaries By Which To Calculate The Positions
        :return: The Position And Dimensions Of The ScrollBar In A Dictionary, False If No Scroll Bar Exists
        """
        browser_window_body_size = self.get_browser_window_body_size()

        browser_inner_size = self.get_browser_inner_size()

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
            utils.fetch_value_percentage(browser_window_body_size.get("height"), window_page_y_offset)) +\
                bot_constants.UP_TASKBAR_HEIGHT

        scroll_bar_width = browser_inner_size.get("width") - browser_window_body_size.get("width")

        if 0 <= scroll_bar_width >= 18:
            scroll_bar_x_position += (scroll_bar_width - 14)
            scroll_bar_width = 14


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

        browser_inner_size = self.get_browser_inner_size()
        browser_window_rect = self.web_browser_driver.get_window_rect()
        web_element_x_offset = web_element_location_dimensions.get("x") + browser_window_rect.get("x") \
                               + (browser_window_rect.get("width") - browser_inner_size["width"]) \
                               - window_page_x_offset
        web_element_y_offset = web_element_location_dimensions.get("y") + browser_window_rect.get("y") \
                               + (browser_window_rect.get("height") - browser_inner_size["height"]) \
                               - window_page_y_offset
        browser_window_rect_bottom = browser_window_rect.get("height") + browser_window_rect.get("y")
        web_element_bottom = web_element_y_offset + web_element_location_dimensions.get("height")
        return {"html_web_element": (web_element_x_offset, web_element_y_offset,
                                     web_element_bottom, web_element_location_dimensions.get("height")),
                "browser_window_rect": (
                    browser_window_rect.get("x"), browser_window_rect.get("y"), browser_window_rect_bottom)}

    def get_document_offset_from_screen(self):
        browser_inner_size = self.get_browser_inner_size()
        browser_window_rect = self.web_browser_driver.get_window_rect()
        return dict(y=browser_window_rect["y"] + (browser_window_rect["height"] - browser_inner_size["height"]),
                    x=browser_window_rect["x"] + (browser_window_rect["width"] - browser_inner_size["width"]))

    def get_element_location_window_offset(self, html_web_element: remote_webdriver.WebElement):
        """
        Calculate And Return Both Element Location Offsets Relative To Window
        :param html_web_element: Target HTML Element
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

    def scroll_element_into_vertical_view(self, html_web_element: remote_webdriver.WebElement, element_scroll_to=1,
                                          simulate_human_behaviour=True):
        """
        This Method Scrolls The Web Page To Put Requested Web Element In View
        :param html_web_element: HTML Web Element To Scroll To
        :param element_scroll_to: Scroll To Top Or Bottom Of Element 1: 0 For Top, 1 For Bottom
        :param simulate_human_behaviour: If Argument Is True, Method Will Attempt To Simulate Human Interaction Scroll
        :return: Return True When Scroll Is Complete
        """
        def has_page_offset_changed():
            document_offsets = self.get_window_document_offsets()
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
            time.sleep(rand.uniform(1.1, 1.75))
            self.keyboard.up(key)
            time.sleep(rand.uniform(0.5, 1.5))

        def scroll_with_touch(direction, duration):
            if direction:
                px_to_adjust_by = rand.randint(1, 500)
            if not direction:
                px_to_adjust_by = rand.randint(-500, -1)
            self.read_with_touch(px_to_adjust_by, duration)

        element_browser_coordinates = \
            self.get_element_window_location_screen_offsets(html_web_element)

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
                        element_browser_coordinates = self.get_element_window_location_screen_offsets(html_web_element)
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
                        element_browser_coordinates = self.get_element_window_location_screen_offsets(html_web_element)

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
                        element_browser_coordinates = self.get_element_window_location_screen_offsets(html_web_element)
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
                        element_browser_coordinates = self.get_element_window_location_screen_offsets(html_web_element)

        else:
            self.browser_action_chains.move_to_element(html_web_element)

    def send_mouse_to_scrollbar(self, is_asychronous=False):
        scroll_bar = self.get_scroll_bar_coordinates(2)
        return self.simulate_human_mouse_move_behavior_to_area(
            scroll_bar['x_pos'] + 2, scroll_bar['y_pos'] + 2, scroll_bar['width'], scroll_bar['height'], rand.randint(0, 100),
            rand.randint(0, 100), 30, rand.uniform(0.4, 1.0),
            is_asychronous)

    def get_window_document_offsets(self):
        return {"y_offset": self.web_browser_driver.execute_script("return window.pageYOffset"),
                "x_offset": self.web_browser_driver.execute_script("return window.pageXOffset")}

    def scroll_to_percentage_in_element(self, html_web_element, percentage_to_scroll_to, time_to_sleep=1):
        def has_page_offset_changed():
            document_offsets = self.get_window_document_offsets()
            document_offsets = [document_offsets["x_offset"], document_offsets["y_offset"]]
            if self.last_document_offsets == document_offsets:
                return False
            else:
                return True

        def random_miscellaneous_key_presses(key_down_probability):
            for i in range(rand.randint(1, 5)):
                if rand.random() < key_down_probability:
                    self.keyboard.down(K_Keys["ArrowDown"])
                else:
                    self.keyboard.down(K_Keys["ArrowUp"])
                time.sleep(rand.uniform(0.05, 0.45))

        def scroll_with_touch(direction, duration):
            if direction:
                px_to_adjust_by = rand.randint(1, 500)
            if not direction:
                px_to_adjust_by = rand.randint(-500, -1)
            self.read_with_touch(px_to_adjust_by, duration)

        def offset_adjuster(offset_to_adjust_to, html_web_element):
            element_coordinates = self.get_element_location_window_offset(html_web_element)
            if offset_to_adjust_to > element_coordinates["y_offset"]:
                if isinstance(self.touch, Touchscreen):
                    while offset_to_adjust_to >= element_coordinates["y_offset"]:
                        if not has_page_offset_changed():
                            return True
                        scroll_with_touch(False, 0.2)
                        element_coordinates = self.get_element_location_window_offset(html_web_element)
                else:
                    while offset_to_adjust_to >= element_coordinates["y_offset"]:
                        self.keyboard.down_persistent(K_Keys["ArrowUp"])
                        if utils.clean_negative(element_coordinates["y_offset"]) - utils.clean_negative(
                                offset_to_adjust_to) \
                                < bot_constants.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT:
                            time.sleep(rand.uniform(0.01, 0.267))
                            self.keyboard.up(K_Keys["ArrowUp"])
                            time.sleep(rand.uniform(0.15, 0.6))
                        else:
                            time.sleep(0.3)
                        element_coordinates = self.get_element_location_window_offset(html_web_element)
                    self.keyboard.up(K_Keys["ArrowUp"])
                    if rand.random() > 0.5:
                        random_miscellaneous_key_presses(0.75)
            elif offset_to_adjust_to < element_coordinates["y_offset"]:
                if isinstance(self.touch, Touchscreen):
                    while offset_to_adjust_to <= element_coordinates["y_offset"]:
                        if not has_page_offset_changed():
                            return True
                        scroll_with_touch(True, 0.2)
                        element_coordinates = self.get_element_location_window_offset(html_web_element)
                else:
                    while offset_to_adjust_to <= element_coordinates["y_offset"]:
                        self.keyboard.down_persistent(K_Keys["ArrowDown"])
                        if utils.clean_negative(offset_to_adjust_to) - utils.clean_negative(
                                element_coordinates["y_offset"]) \
                                < bot_constants.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT:
                            time.sleep(rand.uniform(0.01, 0.267))
                            self.keyboard.up(K_Keys["ArrowDown"])
                            time.sleep(rand.uniform(0.15, 0.6))
                        else:
                            time.sleep(0.3)
                        element_coordinates = self.get_element_location_window_offset(html_web_element)
                    self.keyboard.up(K_Keys["ArrowDown"])
                    if rand.random() > 0.5:
                        random_miscellaneous_key_presses(0.25)

        # Element Height - Browser Window Makes It Possible To Eject Browser Dimensions From Calculations
        workable_height = html_web_element.rect.get("height") - self.web_browser_driver.get_window_rect().get("height")

        offset_to_adjust_to = utils.fetch_percentage_value(workable_height, percentage_to_scroll_to)
        offset_to_adjust_to *= -1

        original_y_offset = self.get_element_location_window_offset(html_web_element)["y_offset"]

        offset_adjuster(offset_to_adjust_to, html_web_element)
        time.sleep(time_to_sleep)
        offset_adjuster(original_y_offset, html_web_element)

    def read_with_arrow_keys(self, html_web_element, boundary, key=K_Keys["ArrowDown"], direction_to_move=True):
        self.keyboard.down_persistent(key)
        element_coordinates = self.get_element_location_window_offset(html_web_element)
        boundary = element_coordinates.get("y_offset") - boundary

        if direction_to_move:
            while element_coordinates.get("y_offset") >= boundary:
                time.sleep(0.1)
                element_coordinates = self.get_element_location_window_offset(html_web_element)

        elif not direction_to_move:
            while element_coordinates.get("y_offset") <= boundary:
                time.sleep(0.1)
                element_coordinates = self.get_element_location_window_offset(html_web_element)
        self.keyboard.up(key)
        return True

    def read_with_mouse_to_scrollbar(self,
                                     coordinates_offset_overshoot={'x': 0, 'y': 0, 'x_offset_percentage': 0,
                                                                   'y_offset_percentage': 0,
                                                                   'max_overshoot': 0, 'probability_of_overshoot': 0},
                                     is_asychronous=False,
                                     counter=0):
        pyautogui.mouseDown()
        self.simulate_human_mouse_move_behavior_to_point(
            coordinates_offset_overshoot['x'], coordinates_offset_overshoot['y'],
            coordinates_offset_overshoot['x_offset_percentage'], coordinates_offset_overshoot['y_offset_percentage'],
            coordinates_offset_overshoot['max_overshoot'], coordinates_offset_overshoot['probability_of_overshoot'],
            True, is_asychronous)
        return counter

    def read_with_touch(self, px_to_adjust_by, duration, force_screen_reset=False):
        # A List Containing The Browser's Page 9-Ways Splitted Dimension In The Following Format
        # [[(x, y, width, height) x3] x3]
        generated_page_boundaries = []
        if not hasattr(self, "generated_page_boundaries") or force_screen_reset:
            a_third_width = self.identity.screen_width / 3
            a_third_height = self.identity.screen_height / 3
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

        window_document = self.get_document_offset_from_screen()
        x_start = x_start if x_start >= 0 else 0
        y_start = y_start if y_start >= 0 else 0
        x_end = x_end if x_end >= 0 else 0
        y_end = y_end if y_end >= 0 else 0

        if not duration:
            duration = rand.uniform(0.1, 2)
        self.touch.simulate_human_touch_movement_with_mouse((x_start, y_start), (x_end, y_end), duration)

    def looper(self, read_time, direction_to_move, html_web_element, total_px_to_adjust_by,
               rem_px_to_adjust_by, rem_read_time, owing_misc_time, mode="arrow_keys", **kwargs):
        element_coordinates = self.get_element_location_window_offset(html_web_element)
        browser_inner_size = self.get_browser_inner_size()
        if rand.randint(0, 1):
            px_to_adjust_by = rand.randint(1, round(browser_inner_size.get("height") / 1.5))
        else:
            px_to_adjust_by = rand.randint(1, round(self.web_browser_driver.get_window_rect().get("height") / 2))
        element_base_offset = element_coordinates.get("y_offset")
        # Update Misc Time
        misc_time = time.time()

        if mode == "arrow_keys":
            multiplier = 1
            if owing_misc_time >= 1:
                multiplier = 2.6
            self.read_with_arrow_keys(html_web_element, px_to_adjust_by * multiplier, K_Keys["ArrowDown"], True)
        elif mode == "wheel":
            self.mouse.mouse_wheel(*pyautogui.position(), px_to_adjust_by, deltaY=self.identity.mouse_delta_y)
        elif mode == "touch":
            read_duration = 2
            if owing_misc_time >= 1:
                read_duration = round(rand.uniform(0.1, 0.3), 2)
            self.read_with_touch(px_to_adjust_by, read_duration)
        elif mode == "mouse_to_scrollbar":
            if "present_mouse_points" in kwargs:
                multiplier = 1
                if owing_misc_time >= 1:
                    multiplier = 2.2
                mouse_x, mouse_y = pyautogui.position()
                mouse_x += utils.fetch_percentage_value(browser_inner_size["height"], rand.randint(-1, 1))
                mouse_y += ((px_to_adjust_by*multiplier / self.web_browser_driver.execute_script(
                    "return document.body.getBoundingClientRect().height")) * browser_inner_size["height"])
                kwargs["present_mouse_points"]["x"] = mouse_x
                kwargs["present_mouse_points"]["y"] = mouse_y
                self.read_with_mouse_to_scrollbar(
                    {'x': mouse_x, 'y': mouse_y, 'x_offset_percentage': 0,
                     'y_offset_percentage': 0, 'max_overshoot': 0, 'probability_of_overshoot': 0})
            else:
                present_mouse_points = self.send_mouse_to_scrollbar()
                if not isinstance(present_mouse_points, dict):
                    raise TypeError(
                        "Set Function Asychronous Parameter To False, If Expecting Dict Of Mouse Coordinates")
                kwargs["present_mouse_points"] = present_mouse_points
                time.sleep(rand.uniform(0, 1))

        # Wait So Browser Can Fully Complete Scroll
        time.sleep(0.12)

        element_coordinates = self.get_element_location_window_offset(html_web_element)
        # Changing The Value Of px_to_adjust_by To The Amount Of px Actually Adjusted
        px_to_adjust_by = (element_base_offset - element_coordinates.get("y_offset"))

        if px_to_adjust_by > rem_px_to_adjust_by:
            px_to_adjust_by = rem_px_to_adjust_by
            rem_px_to_adjust_by = 0
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
        # print(f"Bot Process Id {self.bot_process_id} <:::> Advancing In Read --> Reading Element(Bottom: {element_coordinates['bottom']})")

        time.sleep(round(seconds_to_hang_for, 2))
        if rem_px_to_adjust_by > 0 and element_coordinates.get("bottom") > \
                (browser_inner_size.get("height") + utils.fetch_percentage_value(browser_inner_size.get("height"), 40)):
            self.looper(read_time, direction_to_move, html_web_element, total_px_to_adjust_by,
                        rem_px_to_adjust_by, rem_read_time, owing_misc_time, mode, **kwargs)
        else:
            return True

    def open_link_in_related_articles_section(self, related_articles_sections: remote_webdriver.WebElement):
        links_to_follow = []
        for ras in related_articles_sections:
            for link in ras.find_elements(By.TAG_NAME, "a"):
                link_children = link.find_elements(By.CSS_SELECTOR, "*")
                if len(link_children) >= 1:
                    for link_child in link_children:
                        links_to_follow.append(link_child)
                else:
                    links_to_follow.append(link)
        if WebBot.active_on_mouse_movement.value < 0 and len(links_to_follow) >= 1:
            WebBot.active_on_mouse_movement.value = self.bot_process_id
            print(f"Bot Process Id {self.bot_process_id} <:::> Attempting To Open A Link In Related Articles")
            self.bring_window_to_front()
            link_to_follow = links_to_follow[rand.randint(0, len(links_to_follow) - 1)]
            self.move_pointing_device_to_element(link_to_follow)
            time.sleep(rand.uniform(0.2, 0.8))
            if isinstance(self.touch, Touchscreen):
                time.sleep(rand.uniform(0.3, 0.5))
                element_location_and_dimensions = self.get_element_location_window_offset(link_to_follow)
                self.touch.tap(element_location_and_dimensions["x_offset"] +
                               rand.uniform(0, link_to_follow.rect["width"]),
                               element_location_and_dimensions["y_offset"] +
                               rand.uniform(0, link_to_follow.rect["height"])
                               )
            else:
                pyautogui.click()
            print(f"Bot Process Id {self.bot_process_id} <:::> Done Attempting To Open A Link In Related Articles")
            time.sleep(0.3)
            WebBot.active_on_mouse_movement.value = -self.bot_process_id if self.bot_process_id != 0 else -500
            return True
        return False
    def read_element_content(self, html_web_element: remote_webdriver.WebElement):
        """
        This Method Scrolls The Web Page To Put Requested Web Element In View
        :param html_web_element: HTML Web Element To Scroll To
        :return: Return True When Scroll Is Complete
        """
        time_started = time.time()
        def read(read_time, direction_to_move, html_web_element: remote_webdriver.WebElement,
                 mode, percentage_of_content_to_read=100):
            """
            Send Information To Looper To Read Content By Set Amount Of Content And Time
            :param read_time: Amount Of Time To Move Through Content
            :param direction_to_move: Direction To Read To, True For Down, False For Up
            :param html_web_element: HTML Web Element To Scroll To
            :param mode: Mode Of Naviagation To Use, Usable Values are (arrow_keys, touch, mouse_to_scrollbar, mouse_scroll)
            :param percentage_of_content_to_read: Percentage Of Article Height To Stop At
            :return: True
            """
            # Get The Total Pixels To Move By Using The percentage_of_content_to_read On html_web_element Height
            total_px_to_adjust_by = utils.fetch_percentage_value(
                html_web_element.rect.get("height"),
                percentage_of_content_to_read)
            rem_px_to_adjust_by = total_px_to_adjust_by
            rem_read_time = read_time
            owing_misc_time = 0
            self.looper(read_time, direction_to_move, html_web_element, total_px_to_adjust_by,
                        rem_px_to_adjust_by, rem_read_time, owing_misc_time, mode)

        seconds_to_read = self.calculate_and_generate_page_read_time(html_web_element, self.identity.reading_speed,
                                                                     self.identity.article_read_time_offset)
        content_read_percentage = rand.randint(85, 100)
        print(f"Bot Process Id {self.bot_process_id} <:::> Percentage Of Content To Read And Seconds To Read For: ", content_read_percentage, seconds_to_read)
        self.scroll_element_into_vertical_view(html_web_element, element_scroll_to=0)

        remaining_reading_content_percentage = content_read_percentage
        browser_inner_size = self.get_browser_inner_size()

        mode = ""
        while remaining_reading_content_percentage > 0 and \
                self.get_element_location_window_offset(html_web_element).get("bottom") > (
                browser_inner_size.get("height") +
                utils.fetch_percentage_value(browser_inner_size.get("height"), 40)):
            next_read_sequence_percentage = rand.randint(1, remaining_reading_content_percentage)
            # If Remaining Read Percentage is Lesser Than 6.
            # Assign Remaining Reading Read Percentage To It
            if remaining_reading_content_percentage < 50 and rand.random() < 0.15:
                print(f"Bot Process Id {self.bot_process_id} <:::> Current Activity --> Scrolling To Random Point On Article")
                random_max = 100 - remaining_reading_content_percentage
                self.scroll_to_percentage_in_element(
                    html_web_element, rand.uniform(1, random_max), rand.uniform(0.9, 2))

            next_read_sequence_time = utils.fetch_percentage_value(
                seconds_to_read, next_read_sequence_percentage + rand.uniform(0, 1.2))

            print(f"Bot Process Id {self.bot_process_id} <:::> Remaining Content Percentage To Read -->", remaining_reading_content_percentage)

            # Release Mouse Hold If Mode In Last Read Was Mouse To ScrollBar
            if mode == "mouse_to_scrollbar":
                pyautogui.mouseUp()
                WebBot.active_on_mouse_movement.value = -self.bot_process_id if self.bot_process_id != 0 else -500

            mode = "arrow_keys"
            if isinstance(self.touch, Touchscreen):
                mode = "touch"
            elif isinstance(self.mouse, Mouse):
                mode = "wheel"
                if rand.random() < 0.75 and WebBot.active_on_mouse_movement.value < 0:
                    WebBot.active_on_mouse_movement.value = self.bot_process_id
                    mode = "mouse_to_scrollbar"
                    self.bring_window_to_front()
            elif rand.random() < 0.75 and WebBot.active_on_mouse_movement.value < 0:
                WebBot.active_on_mouse_movement.value = self.bot_process_id
                mode = "mouse_to_scrollbar"
                self.bring_window_to_front()

            if remaining_reading_content_percentage < 6:
                next_read_sequence_percentage = remaining_reading_content_percentage
                remaining_reading_content_percentage = 0
            else:
                remaining_reading_content_percentage -= next_read_sequence_percentage
            print(f"Bot Process Id {self.bot_process_id} <:::> Navigation Mode -->", mode)

            read(next_read_sequence_time, True, html_web_element, mode, next_read_sequence_percentage)
        if mode == "mouse_to_scrollbar":
            pyautogui.mouseUp()
            WebBot.active_on_mouse_movement.value = -self.bot_process_id if self.bot_process_id != 0 else -500
        print(f"ARTICLE READ SESSION COMPLETED, BOT THREAD ID {self.bot_process_id} | TIME SPENT: {time.time() - time_started}")
        return True

    def bring_window_to_front(self):
        self.web_browser_driver.switch_to.window(self.web_browser_driver.current_window_handle)

    def move_mouse_to_fool_exit_point(self):
        if WebBot.active_on_mouse_movement.value < 0:
            WebBot.active_on_mouse_movement.value = self.bot_process_id
            self.bring_window_to_front()
            self.simulate_human_mouse_move_behavior_to_point(rand.randint(0, bot_constants.SCREEN_WIDTH), 4)
            time.sleep(0.5)
            WebBot.active_on_mouse_movement.value = -self.bot_process_id if self.bot_process_id != 0 else -500

    def move_mouse_to_random_area_on_screen(self):
        if WebBot.active_on_mouse_movement.value < 0:
            WebBot.active_on_mouse_movement.value = self.bot_process_id
            self.bring_window_to_front()
            self.simulate_human_mouse_move_behavior_to_area(0, 0,
                                                            bot_constants.SCREEN_WIDTH, bot_constants.SCREEN_HEIGHT,
                                                            x_coordinates_offset_percentage=rand.randint(0, 100),
                                                            y_coordinates_offset_percentage=rand.randint(0, 100),
                                                            max_overshoot=35,
                                                            probability_of_overshoot=round(rand.random(), 2))
            time.sleep(0.5)
            WebBot.active_on_mouse_movement.value = -self.bot_process_id if self.bot_process_id != 0 else -500

    def calculate_and_generate_page_read_time(self, html_web_element_to_read: remote_webdriver.WebElement = None,
                                              reading_speed=700, offset=20):
        """
        A Method To Calculate And Generate an Expected Read Time For Web Text Content Based On Set 'Words Scanning Per
        Minute(WSPM)' With Randomly Generated Offsets At a Max Which Can Be Either Positive or Negative
        :param html_web_element_to_read: Element Containing Web Text Content To Read On. If None, Method Tries To
        Fetch The Article Element Of The Web Page
        :param reading_speed: The Set Reading Speed Of Which Calculations Will Be Performed Upon.
        :param max_offset: The Maximum Percentage A Randomly Generated Offset Can Attain Either Positive or Negative
        :return: Returns Amount Of Seconds To Read Content For
        """
        if not html_web_element_to_read:
            html_web_element_to_read = self.web_browser_driver.find_element(By.TAG_NAME, "article")

        all_element_words = html_web_element_to_read.text.split()
        words_len = len(all_element_words)
        seconds_to_read = (words_len / reading_speed) * 60
        seconds_to_read += (seconds_to_read * offset / 100)

        # Convert To Seconds And Return
        return round(seconds_to_read)

    def move_pointing_device_to_element(self, html_web_element: remote_webdriver.WebElement, simulate_human_behaviour=True):
        """
        :param html_web_element: HTML Element to Move To
        :param simulate_human_behaviour: If Bool is True(Which is By Default) use pyAutoGUI to Simulate Human Behaviour
        :return: return true on success
        """
        if simulate_human_behaviour:
            self.scroll_element_into_vertical_view(html_web_element, element_scroll_to=1)
            if not isinstance(self.touch, Touchscreen):
                element_screen_position = self.get_element_window_location_screen_offsets(html_web_element)
                el_pos = dict(area_x=element_screen_position["html_web_element"][0],
                              area_y=element_screen_position["html_web_element"][1],
                              area_width=html_web_element.rect["width"],
                              area_height=html_web_element.rect["height"])

                self.simulate_human_mouse_move_behavior_to_area(el_pos["area_x"]+1, el_pos["area_y"]+1,
                                                                el_pos["area_width"]-2, el_pos["area_height"]-2,
                                                                x_coordinates_offset_percentage=rand.randint(0, 100),
                                                                y_coordinates_offset_percentage=rand.randint(0, 100),
                                                                max_overshoot=35,
                                                                probability_of_overshoot=round(rand.random(), 2))
        else:
            self.browser_action_chains.move_to_element_with_offset(html_web_element, 20, 20).perform()

    def inject_referer_into_header(self, request: request.Request):
        if self.referer_use_times < 1:
            del request.headers['Referer']
            request.headers.add_header("Referer", self.identity.referer)
            self.referer_use_times += 1

    def inject_js_to_spoof_fingerprintable_objects_on_website_server_response(
            self, request: request.Request, response: request.Response):
        """
        A Method
        :param: The Orginal Request
        :param response: The Response of The Web Server To Adjust Before Reaching Browser
        :return: True On Success, False On Failure
        """
        if response:
            try:
                if ((response.headers.get('content-type').find('text/html') or
                     not re.search(r'(?<!https:)(?<!https:/)(\/\w)$', request.url) or re.match(r'(.html|.htm)$',
                                                                                               request.url))
                        and request.method == 'GET' and response.status_code == 200):
                    body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
                    body = body.decode('utf-8')
                    if body.find("<!DOCTYPE") == 0 or body.find("<html") == 0 or body.find("<!--") == 0:
                        if self.identity.has_battery == "has_battery":
                            has_battery = True
                        else:
                            has_battery = False
                        fingerprintables_spoof_code = utils.return_fingerprintables_spoof_js_code(
                            offset_color_value=tuple(self.identity.canvas_fp_offset),
                            audio_context_offset=self.identity.audio_context_fp_offset,
                            webgl_params=(self.identity.gpu_vendor, 15, 12, 14, 14, 13, 4, 4, 4, 4, 3, 3, 3, 3, 6, 11, 12, 12,
                                          self.identity.gpu_renderer), timezone=self.identity.timezone,
                            font_width_offset=self.identity.font_fp_offset[0],
                            font_height_offset=self.identity.font_fp_offset[1],
                            hardware_specs={"hardware_concurrency": self.identity.hardware_concurrency,
                                            "memory": self.identity.memory},
                            has_battery=has_battery, referer=self.identity.referer)
                        self.identity.referer = ""
                        if isinstance(body, str):
                            if body.find("<head>") != -1:
                                body = utils.insert_text_into_string(
                                    body,
                                    "<script>" + fingerprintables_spoof_code + "</script>",
                                    "<head>", True)
                            else:
                                body = utils.insert_text_into_string_reg(
                                    body, fingerprintables_spoof_code, r"(<script>)|(<script .*?>)", True)
                            body = body.encode()
                            body = encoding.encode(body, response.headers.get('Content-Encoding', 'identity'))
                            if "content-length" in response.headers:
                                response.headers.replace_header("content-length", str(len(body)))
                            response.body = body
                            return True
            except Exception:
                pass
            self.identity.referrer = ""
        return False
    
    def quit_browser_after_max_alive(self, sleep_time=bot_constants.BOT_MIN_ALIVE_TIME):
        time.sleep(sleep_time)
        if hasattr(self, "web_browser_driver"):
            if time.time() - self.time_activated > bot_constants.BOT_MAX_ALIVE_TIME + rand.uniform(-6.5, 6.5):
                print(f"{self.identity.id} On Process {self.bot_process_id} Could Not Perform "
                      f"Activity Within Set Time, Exiting Session...")
                print(f"Bot Process Id {self.bot_process_id} <:::> Updating Cookies To Cloud")
                self.update_cookies_to_cloud()
                self.web_browser_driver.quit()
                del self.web_browser_driver
                del self
            else:
                self.quit_browser_after_max_alive(sleep_time=5)

    def open_web_browser(self):
        open_browser_in_full_screen = True
        window_size = (bot_constants.SCREEN_WIDTH, bot_constants.SCREEN_HEIGHT)
        if rand.random() < 0.05 and self.identity.device_type == "is_pc":
            open_browser_in_full_screen = False
            window_size = utils.fetch_random_window_size_relative_to_screen(
                bot_constants.SCREEN_WIDTH, bot_constants.SCREEN_HEIGHT)
        if self.browser_to_use_id == browser_constants.CHROME_ID:
            print(f"Bot Process Id {self.bot_process_id} <:::> Opening Chrome Browser")
            browser_options = webdriver.ChromeOptions()
            browser_options.binary_location = browser_constants.CHROME_BINARY_LOCATION
            if open_browser_in_full_screen:
                browser_options.add_argument("--start-maximized")
            else:
                browser_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
            self.web_browser_driver = sw_uc.Chrome(
                driver_executable_path=self.driver_path, options=browser_options)
        elif self.browser_to_use_id == browser_constants.FIREFOX_ID:
            browser_options = webdriver.FirefoxOptions()
            browser_options.binary_location = browser_constants.FIREFOX_BINARY_LOCATION
            firefox_profile = webdriver.FirefoxProfile("")
            firefox_profile.update_preferences()
            self.web_browser_driver = webdriver.Firefox(
                executable_path=self.driver_path, options=browser_options, firefox_profile=firefox_profile,
                desired_capabilities=DesiredCapabilities.FIREFOX)
        print(f"Bot Process Id {self.bot_process_id} <:::> Web Browser Opened")
        print(f"Bot Process Id {self.bot_process_id} <:::> Activating Browser Based On Device Type")
        if self.identity.device_type == "is_smartphone":
            print(f"Bot Process Id {self.bot_process_id} <:::> Device Name:", self.identity.hardware)
            devtools_primary.activate_mobile(self.web_browser_driver,
                                             {"width": self.identity.screen_width,
                                              "height": self.identity.screen_height, "deviceScaleFactor":
                                                  self.identity.screen_resolution[4], "screenOrientation":
                                                  {"type": "portraitPrimary", "angle": 0},
                                              "mobile": True})
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Page To Always Be In Focus")
        devtools_primary.activate_all_focus(self.web_browser_driver)
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Cookies From Identity")
        devtools_primary.set_all_cookies(self.web_browser_driver, self.identity.cookies)
        if self.identity.user_agent:
            print(f"Bot Process Id {self.bot_process_id} <:::> Setting User Agent From Identity")
            devtools_primary.change_user_agent(
                self.web_browser_driver,
                self.identity.user_agent, self.identity.platform)
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Timezone From Identity")
        devtools_primary.set_timezone(self.web_browser_driver, self.identity.timezone[0])
        self.browser_action_chains = ActionChains(self.web_browser_driver)
        self.keyboard = Keyboard(self.web_browser_driver)
        if self.identity.has_touch == "has_touch":
            self.touch = Touchscreen(self.web_browser_driver, self.keyboard)
        self.web_browser_driver.implicitly_wait(bot_constants.IMPLICITLY_WAIT_TIME)
        if open_browser_in_full_screen:
            self.web_browser_driver.maximize_window()
        else:
            self.web_browser_driver.set_window_position(0, 0)
            self.web_browser_driver.set_window_size(*window_size)
        self.web_browser_driver.request_interceptor = self.inject_referer_into_header
        self.web_browser_driver.response_interceptor = \
            self.inject_js_to_spoof_fingerprintable_objects_on_website_server_response
        Thread(target=self.quit_browser_after_max_alive).start()


    def fetch_all_cookies(self):
        return devtools_primary.get_all_cookies(self.web_browser_driver)

    def set_all_cookies(self, cookies):
        devtools_primary.set_all_cookies(cookies)
        return True

    def update_cookies_to_cloud(self):
        self.identity.update_cookies(self.fetch_all_cookies())

    def open_new_tab(self, url):
        """
        :param url: Url Location Of The WebPage
        :return: Return True On Success
        """
        try:
            self.web_browser_driver.execute_script(f"window.open();")
            self.web_browser_driver.switch_to.window(self.web_browser_driver.window_handles[-1])
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
                print(
                    url_name + " is identifying a url already, use another url name or resolve code to select more unique name")
                return False
            else:
                if not self.opened_browser_urls:  # If first Url To Browser,
                    # Open New And Terminate First Because It Has No Name Identifier
                    self.opened_browser_urls[url_name] = self.web_browser_driver.window_handles[0]
                    self.web_browser_driver.get(url)
                else:
                    url_id = self.open_new_tab(url)
                    if url_id:
                        self.opened_browser_urls[url_name] = url_id
                        print(self.opened_browser_urls)
                    else:
                        print(f"Bot Process Id {self.bot_process_id} <:::> Unable To Open Url: " + url + ", With Name: " + url_name)
                    return True
        elif force_browser_diversion:
            """Create A Method That Checks All Other Opened Browsers To 
        Open The Url Incase Chrome Isn't Alive"""
        else:
            raise NameError("No Available Chrome Browser, Either Set One Up by Using The "
                            "'open_web_browser_driver' or Force Browser Diversion")
        return False

    def __exit__(self):
        print(f"Bot Process Id {self.bot_process_id} <:::> Cookies: ", devtools_primary.get_all_cookies(self.web_browser_driver))
