# With Great Power Comes Great Responsibility

# Standard Library Imports
import os
import ctypes
import random
import re
import pytweening
import random as rand
import json
import tempfile
from functools import reduce

from requests.exceptions import SSLError, ProxyError
from threading import Thread
from multiprocessing import Value
import requests_cache as cached_requests
import requests as main_requests
# External Python Packages
import time

import seleniumwire.undetected_chromedriver.v2 as sw_uc
from seleniumwire import webdriver, request
from seleniumwire.utils import decode
from seleniumwire.thirdparty.mitmproxy.net.http import encoding
from selenium.webdriver.remote import webdriver as remote_webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException, InvalidArgumentException
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
            bot_process_id=None,
            no_of_clicks=0
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
        self.no_of_clicks = no_of_clicks
        self.probability_of_click = 0.45
        self.current_tab_length = 1
        self.cached_requests_session = cached_requests.CachedSession(
            bot_constants.FULL_DIRECTORY_PATH + '/caches/request_caches/requests_cache')
        self.requests_session = cached_requests.CachedSession(
            bot_constants.FULL_DIRECTORY_PATH + '/caches/request_caches/proxy_requests_cache', cache_control=True)
        self.total_request_size = 0
        self.uncached_response_size = 0
        self.cached_response_size = 0
        self.url_through_proxy_response_size = 0
        self.urls_cached = set()
        self.urls_through_proxy = set()
        self.proxy = None
        self.ad_to_click = False
        self.ad_with_keyword_wait_counter = 0

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
            duration = rand.uniform(0.2, 1.2)
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
            duration = rand.uniform(0.2, 1.2)
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

            print(f"Bot Process Id {self.bot_process_id} <:::> Mouse Moved To: ", x_coordinates_to_move_to,
                  y_coordinates_to_move_to)
            return {'x': int(x_coordinates_to_move_to), 'y': int(y_coordinates_to_move_to)}

        if move_to_new_thread:
            t = Thread(target=move_operations)
            t.daemon = True
            return t.start()
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
            utils.fetch_value_percentage(browser_window_body_size.get("height"), window_page_y_offset)) + \
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
        """
        This method calculates the dimensions of the document page of a browser relative to the screen
        :return: A dictionary holding document dimensions
        """
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
            scroll_bar['x_pos'] + 2, scroll_bar['y_pos'] + 2, scroll_bar['width'], scroll_bar['height'],
            rand.randint(0, 100),
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
                        scroll_with_touch(False, 0.5)
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
                        scroll_with_touch(True, 0.5)
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
        old_element_coordinates = element_coordinates
        boundary = element_coordinates.get("y_offset") - boundary
        offset_same_count = 0

        if direction_to_move:
            while element_coordinates.get("y_offset") >= boundary:
                old_element_coordinates = self.get_element_location_window_offset(html_web_element)
                time.sleep(0.1)
                element_coordinates = self.get_element_location_window_offset(html_web_element)

                if offset_same_count > 1:
                    break
                if element_coordinates.get("y_offset") == old_element_coordinates.get("y_offset"):
                    offset_same_count += 1

        elif not direction_to_move:
            while boundary >= element_coordinates.get("y_offset"):
                old_element_coordinates = self.get_element_location_window_offset(html_web_element)
                time.sleep(0.1)
                element_coordinates = self.get_element_location_window_offset(html_web_element)

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
        if self.no_of_clicks > 0:
            while self.revert_to_main_page():
                pyautogui.mouseUp()
                pyautogui.mouseDown()

        self.simulate_human_mouse_move_behavior_to_point(
            coordinates_offset_overshoot['x'], coordinates_offset_overshoot['y'],
            coordinates_offset_overshoot['x_offset_percentage'], coordinates_offset_overshoot['y_offset_percentage'],
            coordinates_offset_overshoot['max_overshoot'], coordinates_offset_overshoot['probability_of_overshoot'],
            True, is_asychronous)
        pyautogui.mouseUp()
        return counter

    def read_with_touch(self, px_to_adjust_by, duration=rand.uniform(0.1, 2), force_screen_reset=False):
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

        x_start = x_start if x_start >= 0 else 0
        y_start = y_start if y_start >= 0 else 0
        x_end = x_end if x_end >= 0 else 0
        y_end = y_end if y_end >= 0 else 0

        self.touch.simulate_human_touch_movement_with_mouse((x_start, y_start), (x_end, y_end), duration)
        self.smart_click_trigger((x_start, y_start), self.identity.device_type)
        self.revert_to_main_page()

    def trigger_vignette(self, open_vignette=False):
        try:
            if not open_vignette:
                ads_dimensions = self.locate_ad_elements_in_iframe(ads_elements_type=self.vignette_ad_close_type,
                    ads_elements_name=self.vignette_ad_close_name)
            else:
                ads_dimensions = self.locate_ad_elements_in_iframe(ads_elements_type=self.vignette_ad_open_type,
                                                                   ads_elements_name=self.vignette_ad_open_name)
            if not ads_dimensions:
                return
            time.sleep(0.5)
            if not open_vignette:
                self.ad_click(rand.choice(ads_dimensions), revert_back=False)
            else:
                self.ad_click(rand.choice(ads_dimensions))
            print(f"Bot Process Id {self.bot_process_id} <:::> Vignette ad trigger attempted")
            time.sleep(0.5)
            self.trigger_vignette()
        except TimeoutException:
            # I no longer use Expected conditions in the iframe_check for locating elements, so this branch of code may never be reached, look for other ways
            print(f"Bot Process Id {self.bot_process_id} <:::> No active vignette to close")
            return

    def smart_ad_click(self, switch_focus_to_new_tab=True):
        ad_click_success = False
        if not hasattr(self, "track_vignette_close"):
            self.track_vignette_close = 1
        if self.ad_to_click != "vignette" and self.vignette_ad_close_name and self.track_vignette_close >= 3:
            self.trigger_vignette()
            self.track_vignette_close = 0
        else:
            self.track_vignette_close += 1
        tab_length = len(self.web_browser_driver.window_handles)
        try:
            if self.ad_to_click == "vignette" and self.vignette_ad_open_name:
                # Reseting time activated before loading, so ad page has more time to load
                self.time_activated = time.time()
                self.trigger_vignette(open_vignette=True)
                if tab_length != len(self.web_browser_driver.window_handles):
                    self.ad_to_click = None
                    ad_click_success = True
            elif self.ad_to_click == "in_page" and self.in_page_ad_links_name:
                self.trigger_vignette()
                time.sleep(0.4)
                ads_dimensions = self.locate_ad_elements_in_iframe(ads_elements_type=self.in_page_ad_links_type,
                                                         ads_elements_name=self.in_page_ad_links_name)
                if not ads_dimensions:
                    return

                if not isinstance(self.ad_keywords, list) or self.ad_with_keyword_wait_counter >= 1:
                    print(f"Bot Process Id {self.bot_process_id} <:::> Keywords won't be used as basis for ad click")
                    # Reseting time activated before loading, so ad page has more time to load
                    self.time_activated = time.time()
                    if self.ad_click(rand.choice(ads_dimensions)) and tab_length != len(self.web_browser_driver.window_handles):
                        ad_click_success = True
                        self.ad_to_click = None
                else:
                    for ad_dimensions in ads_dimensions:
                        for keyword in self.ad_keywords:
                            if keyword in ad_dimensions["text_content"]:
                                # Reseting time activated before loading, so ad page has more time to load
                                self.time_activated = time.time()
                                if self.ad_click(ad_dimensions) and tab_length != len(self.web_browser_driver.window_handles):
                                    ad_click_success = True
                                    self.ad_to_click = None
                                print(
                                    f"Bot Process Id {self.bot_process_id} <:::> Keyword was used as a base to click an ad")
                                break
                        else:
                            continue
                        break
                    if self.ad_to_click:
                        self.ad_with_keyword_wait_counter += 1
                        print(f"Bot Process Id {self.bot_process_id} <:::> Ad with any of keywords wasn't found, Try again")
            if ad_click_success and switch_focus_to_new_tab:
                time.sleep(1)
                self.web_browser_driver.switch_to.window(
                    self.web_browser_driver.window_handles[-1])
            if self.identity.device_type == "is_smartphone":
                self.activate_mobile()
            return ad_click_success
        except TimeoutException:
            print(f"Bot Process Id {self.bot_process_id} <:::> No ads found, Try again")

    def ad_click(self, ad_dimensions: dict, revert_back=False):
        if self.identity.device_type == "is_pc":
            previous_mouse_pos = pyautogui.position()
            self.simulate_human_mouse_move_behavior_to_area(ad_dimensions["x"], ad_dimensions["y"],
                                                            ad_dimensions["width"], ad_dimensions["height"],
                                                            x_coordinates_offset_percentage=rand.randint(0, 100),
                                                            y_coordinates_offset_percentage=rand.randint(0, 100),
                                                            max_overshoot=35,
                                                            probability_of_overshoot=round(rand.random(), 2))
            pyautogui.click()
            if revert_back:
                self.revert_to_main_page()
            self.simulate_human_mouse_move_behavior_to_point(previous_mouse_pos[0], previous_mouse_pos[1])
            return True
        elif self.identity.device_type == "is_smartphone":
            self.touch.tap(ad_dimensions["x"] +
                           rand.uniform(0, ad_dimensions["width"]),
                           ad_dimensions["y"] +
                           rand.uniform(0, ad_dimensions["height"])
                           )
            if revert_back:
                self.revert_to_main_page()
            return True

    def locate_ad_elements_in_iframe(self, ads_elements_type, ads_elements_name: str):
        def iframe_check():
            try:
                iframe = self.web_browser_driver.find_element(By.TAG_NAME, "iframe")
                if self.identity.device_type == "is_smartphone":
                    iframe_offset = self.get_element_location_window_offset(iframe)
                else:
                    iframe_offset = self.get_element_window_location_screen_offsets(iframe)["html_web_element"]
                self.web_browser_driver.switch_to.frame(iframe)
            except (WebDriverException, StaleElementReferenceException):
                self.web_browser_driver.switch_to.default_content()
                return False
            ads_elements = None
            try:
                ads_elements = self.web_browser_driver.find_elements(ads_elements_type, ads_elements_name)
            except (TimeoutException, InvalidArgumentException):
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> Element parent body was found but ad elements to interact with were not present")
                self.web_browser_driver.switch_to.default_content()
            if not ads_elements:
                self.web_browser_driver.switch_to.default_content()
                return
            ads_elements_rect = []
            for ad_element in ads_elements:
                rect = ad_element.rect.copy()
                if self.identity.device_type == "is_smartphone":
                    rect["x"] = iframe_offset["x_offset"] + rect["x"]
                    rect["y"] = iframe_offset["y_offset"] + rect["y"]
                else:
                    rect["x"] = iframe_offset[0] + rect["x"]
                    rect["y"] = iframe_offset[1] + rect["y"]
                rect["text_content"] = ad_element.text
                ads_elements_rect.append(rect)
            self.web_browser_driver.switch_to.default_content()
            return ads_elements_rect

        if ads_elements_type == "xpath":
            ads_elements_type = By.XPATH
        elif ads_elements_type == "class":
            ads_elements_type = By.CLASS_NAME
        elif ads_elements_type == "id":
            ads_elements_type = By.ID
        else:
            print(f"Bot Process Id {self.bot_process_id} <:::> The ads type you are trying to locate is not supported")
            return
        if ads_elements_name.startswith("//iframe"):
            ads_elements_name = ads_elements_name[8:]
            return iframe_check()

    def click_trigger(self, x_coord=50, y_coord=50, device_type="is_pc"):
        if device_type == "is_smartphone":
            self.touch.tap(x_coord, y_coord)
            return True
        elif device_type == "is_pc":
            pyautogui.click()
            return True
        else:
            print(
                f"Bot Process Id {self.bot_process_id} <:::> The device type you are attempting to click on is unknown")
            return False

    def smart_click_trigger(self, coords=(100, 100), device_type="is_pc"):
        if self.no_of_clicks > 0:
            if rand.uniform(0, 1) <= self.probability_of_click:
                self.probability_of_click -= utils.fetch_percentage_value(self.probability_of_click, 15)
                self.no_of_clicks -= 1
                self.click_trigger(coords[0], coords[1], device_type)
                print(f"Bot Process Id {self.bot_process_id} <:::> Click was triggered successfully")
                return True
            else:
                self.probability_of_click += utils.fetch_percentage_value(self.probability_of_click, 15)
                return False
        return False

    def set_ad_behaviour_environment(self, ad_to_click, vignette_ad_close_type, vignette_ad_close_name, vignette_ad_open_type,
                vignette_ad_open_name, in_page_ad_links_type, in_page_ad_links_name, maximum_no_of_ads=1, ad_keywords=None):
        self.ad_to_click = ad_to_click

        self.vignette_ad_close_type = vignette_ad_close_type
        self.vignette_ad_close_name = vignette_ad_close_name
        self.vignette_ad_open_type = vignette_ad_open_type
        self.vignette_ad_open_name = vignette_ad_open_name

        self.in_page_ad_links_type = in_page_ad_links_type
        self.in_page_ad_links_name = in_page_ad_links_name
        self.maximum_no_of_ads = maximum_no_of_ads
        self.ad_keywords = ad_keywords

    def read_by_mode(self, html_web_element: remote_webdriver.WebElement, px_to_adjust_by, mode="arrow_keys",
                     direction=True, **kwargs):
        px_to_adjust_by = max(px_to_adjust_by, 10)
        # Stamp the initial time before reading began
        read_mode_time_used = time.time()
        if mode == "arrow_keys":
            key = K_Keys["ArrowDown"]
            if not direction:
                key = K_Keys["ArrowUp"]
            self.read_with_arrow_keys(html_web_element, px_to_adjust_by, key, direction)
            # Wait to complete scroll
            time.sleep(0.12)
        elif mode == "wheel":
            self.mouse.mouse_wheel(*pyautogui.position(), px_to_adjust_by, deltaY=self.identity.mouse_delta_y)
        elif mode == "touch":
            if not direction:
                px_to_adjust_by *= -1
            self.read_with_touch(px_to_adjust_by)
        elif mode == "mouse_to_scrollbar":
            def read_with_mouse_to_scrollbar():
                browser_inner_size_height = self.get_browser_inner_size()["height"]
                mouse_x, mouse_y = pyautogui.position()
                mouse_x += utils.fetch_percentage_value(browser_inner_size_height, rand.randint(0, 1))
                px_to_adjust_mouse_y_by = max(((px_to_adjust_by / self.web_browser_driver.execute_script(
                    "return document.body.getBoundingClientRect().height")) * browser_inner_size_height), 3)
                if not direction:
                    px_to_adjust_mouse_y_by *= -1
                mouse_y += px_to_adjust_mouse_y_by
                print("mouse_y ==>", mouse_y)
                kwargs["present_mouse_points"]["x"] = mouse_x
                kwargs["present_mouse_points"]["y"] = mouse_y
                self.read_with_mouse_to_scrollbar(
                    {'x': mouse_x, 'y': mouse_y, 'x_offset_percentage': 0,
                     'y_offset_percentage': 0, 'max_overshoot': 0, 'probability_of_overshoot': 0})

            if "present_mouse_points" in kwargs:
                read_with_mouse_to_scrollbar()
            else:
                present_mouse_points = self.send_mouse_to_scrollbar()
                if not isinstance(present_mouse_points, dict):
                    raise TypeError(
                        "Set Function Asychronous Parameter To False, If Expecting Dict Of Mouse Coordinates")
                kwargs["present_mouse_points"] = present_mouse_points
                time.sleep(rand.uniform(0, 1))
                read_with_mouse_to_scrollbar()
        kwargs["read_mode_time_used"] = time.time() - read_mode_time_used
        return kwargs

    def smart_human_like_content_navigator(self, read_time, html_web_element, total_px_to_adjust_by,
                                           mode="arrow_keys", **kwargs):
        # This is to make up for the edge case, in the event there is no reason to simulate a read
        if total_px_to_adjust_by <= 0:
            time.sleep(read_time)
            return True
        # Stamping the initial time before content will be read or adjusted by with px_to_adjust_by
        read_mode_initial_time_stamp = time.time()

        if self.smart_ad_click():
            return "ad_clicked"

        element_coordinates = self.get_element_location_window_offset(html_web_element)
        browser_inner_size = self.get_browser_inner_size()

        element_base_offset = element_coordinates.get("y_offset")

        # The number of seconds to spend on each px
        avg_time_per_px = read_time / total_px_to_adjust_by

        px_adjusted_by = kwargs.get("px_adjusted_by", 0)
        if px_adjusted_by > total_px_to_adjust_by:
            px_adjusted_by = total_px_to_adjust_by
        read_mode_time_used = kwargs.get("read_mode_time_used", 0)
        time_allocated_to_px_adjusted_by = min(avg_time_per_px * px_adjusted_by, read_time)
        time_allocated_time_used_margin = time_allocated_to_px_adjusted_by - read_mode_time_used

        # print("px adjusted by ===>", px_adjusted_by)
        # print("total px to adjust by ===>", total_px_to_adjust_by)
        # print("read time ===>", read_time)
        # print("time expected to have used based on px adjusted ==>", time_allocated_to_px_adjusted_by)
        # print("time expected time used margin ==>", time_allocated_time_used_margin)

        time_to_pause_activity = 0
        # if the margin between time allocated and time used to read is lesser than 0, do not wait and amplify
        # px_to_adjust_by
        if time_allocated_time_used_margin <= 0:
            # Unlike calculation used for px_to_adjust_by below,amplify by setting destination to the lower ends of page
            px_to_adjust_by = round(rand.uniform(
                browser_inner_size.get("height") / 1.4, browser_inner_size.get("height")))

            # Makes sure px_to_adjust_by is never greater than rem_px_to_adjust_by or total_px_to_adjust_by to try and
            # put a lid on overshooting
            if kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by) < px_to_adjust_by:
                px_to_adjust_by = kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by)
        else:
            # Use Portion of The Browser Inner Size to Determine How Long to Adjust PX by, and if the remaining px to
            # adjust by is lesser than the browser inner size to use, use it so the navigation doesn't scroll the
            # element out of desired offset
            px_to_adjust_by = round(rand.uniform(
                1, browser_inner_size.get("height") / 1.4))

            # Makes sure px_to_adjust_by is never greater than rem_px_to_adjust_by or total_px_to_adjust_by to try and
            # put a lid on overshooting
            if kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by) < px_to_adjust_by:
                px_to_adjust_by = kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by)

            # This is the time activity will be suspended for as thou it's trying to human read the content
            time_to_pause_activity = time_allocated_time_used_margin

            # navigate up as thou looking for forgotten content, feature to reinforce human reading behaviour
            if rand.random() < 0.2:
                # Humans might wait at very different durations before scrolling up to check for some content-text,
                # the sleep below attempts to simulate that by taking no more than a minimal amount which would
                # inavertly affect the read_mode_time_used
                time_to_randomly_wait_before_scrolling_up = random.uniform(0.01, time_to_pause_activity * 0.17)
                time.sleep(time_to_randomly_wait_before_scrolling_up)

                px_to_move_by = browser_inner_size.get("height") * rand.uniform(0.15, 0.35)

                kwargs["read_by_mode_data"] = self.read_by_mode(html_web_element, px_to_move_by, mode, False,
                                                                **kwargs.get("read_by_mode_data", {}))

                # modifying time_to_pause_activity on how long to wait for after navigating up. expected mean time to
                # be around 45% which averagely should not be more than half of time_to_pause_activity
                time_to_pause_activity = utils.fetch_percentage_value(
                    time_to_pause_activity, rand.uniform(35, 55) - (
                            + (kwargs["read_by_mode_data"]["read_mode_time_used"])
                            + time_to_randomly_wait_before_scrolling_up / 2))

                #    print("Time to pause activity one ==>", time_to_pause_activity)
                time.sleep(max(0, time_to_pause_activity))

                # Attempt to return page to original point before going up
                kwargs["read_by_mode_data"] = self.read_by_mode(html_web_element, px_to_move_by, mode, True,
                                                                **kwargs.get("read_by_mode_data", {}))

                # Recalibrate time_to_pause_activity and deduct time used navigating down
                time_to_pause_activity = time_allocated_time_used_margin - (
                        time_to_pause_activity + kwargs["read_by_mode_data"]["read_mode_time_used"] +
                        time_to_randomly_wait_before_scrolling_up / 2)

                #    print("Time to pause activity two ==>", time_to_pause_activity)

                # Finally sleep for the remaining time if remaining
                time.sleep(max(0, time_to_pause_activity))
            else:
                time.sleep(time_to_pause_activity)

        # Store read_by_mode data at each function iteration to be repassed, reason is for read_by_mode
        # mouse_to_scrollbar mode
        kwargs["read_by_mode_data"] = self.read_by_mode(html_web_element, px_to_adjust_by, mode, True,
                                                        **kwargs.get("read_by_mode_data", {}))

        # Recalculating read_mode_time_used to show time spent adjusting or navigating the content,
        # recur time_allocated_time_used_margin to it if in deficit, so it doesn't forget it's behind if so,
        # adding time_to_pause_activity to offset the time waited for and leave only read_mode_time_used
        kwargs["read_mode_time_used"] = (time.time() - read_mode_initial_time_stamp) + time_to_pause_activity

        # print("read mode duration ==>", read_mode_time_used)

        element_coordinates = self.get_element_location_window_offset(html_web_element)
        # Changing The Value Of px_to_adjust_by To The Amount Of px Actually Adjusted
        kwargs["px_adjusted_by"] = (element_base_offset - element_coordinates.get("y_offset"))
        # Calculating Remaining Px, making sure that it's not lesser than 0 at any given point
        kwargs["rem_px_to_adjust_by"] = kwargs.get("rem_px_to_adjust_by", total_px_to_adjust_by) - px_adjusted_by

        # print("remaining px to adjust by ==>", kwargs["rem_px_to_adjust_by"])

        if kwargs["rem_px_to_adjust_by"] <= 0:
            return True

        if kwargs.get("px_adjusted_at_0_count", 0) > 1:
            return True

        if px_adjusted_by == 0:
            kwargs["px_adjusted_at_0_count"] = kwargs.get("px_adjusted_at_0_count", 0) + 1
        else:
            kwargs["px_adjusted_at_0_count"] = 0

        return self.smart_human_like_content_navigator(read_time, html_web_element, total_px_to_adjust_by,
                                                       mode, **kwargs)

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
                try:
                    element_location_and_dimensions = self.get_element_location_window_offset(link_to_follow)
                    # Do click continually until page remained unchanged after click
                    self.touch.tap(element_location_and_dimensions["x_offset"] +
                                   rand.uniform(0, link_to_follow.rect["width"]),
                                   element_location_and_dimensions["y_offset"] +
                                   rand.uniform(0, link_to_follow.rect["height"])
                                   )
                    while self.revert_to_main_page():
                        self.touch.tap(element_location_and_dimensions["x_offset"] +
                                       rand.uniform(0, link_to_follow.rect["width"]),
                                       element_location_and_dimensions["y_offset"] +
                                       rand.uniform(0, link_to_follow.rect["height"])
                                       )
                except StaleElementReferenceException:
                    print(f"Bot Process Id {self.bot_process_id} <:::> An attempt to click on a link in the related "
                          f"article section cause a StaleElementReference error. This is most likely the result of "
                          f"external interaction with the browser that forced a new tab to open without script "
                          f"awareness")
            else:
                # Do click continually until page remained unchanged after click
                pyautogui.click()
                while self.revert_to_main_page():
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
        # There is a potential that the browser inner size might not be fully deducted from the content height to read
        # from. Therefore the remaining should be adjusted unto the rest
        px_owing = -self.get_browser_inner_size()["height"]

        def read(read_time, html_web_element: remote_webdriver.WebElement, mode, percentage_of_content_to_read=100):
            """
            Send Information To Looper To Read Content By Set Amount Of Content And Time
            :param read_time: Amount Of Time To Move Through Content
            :param direction_to_move: Direction To Read To, True For Down, False For Up
            :param html_web_element: HTML Web Element To Scroll To
            :param mode: Mode Of Naviagation To Use, Usable Values are (arrow_keys, touch, mouse_to_scrollbar, mouse_scroll)
            :param percentage_of_content_to_read: Percentage Of Article Height To Stop At
            :return: True
            """
            nonlocal px_owing
            # Get The Total Pixels To Move By Using The percentage_of_content_to_read On html_web_element Height
            total_px_to_adjust_by = utils.fetch_percentage_value(
                html_web_element.rect["height"],
                percentage_of_content_to_read) + px_owing
            px_owing = min(0, total_px_to_adjust_by)
            return self.smart_human_like_content_navigator(read_time, html_web_element, total_px_to_adjust_by, mode)

        seconds_to_read = self.calculate_and_generate_page_read_time(html_web_element, self.identity.reading_speed,
                                                                     self.identity.article_read_time_offset)
        content_read_percentage = rand.randint(85, 100)
        print(f"Bot Process Id {self.bot_process_id} <:::> Percentage Of Content To Read And Seconds To Read For: ",
              content_read_percentage, seconds_to_read)
        self.scroll_element_into_vertical_view(html_web_element, element_scroll_to=0)
        px_owing += self.get_element_location_window_offset(html_web_element).get("y_offset")
        # This sleep is to simulate a pause at the beginning of the article
        time.sleep(random.uniform(2.45, 5.24))
        remaining_reading_content_percentage = content_read_percentage
        browser_inner_size = self.get_browser_inner_size()

        mode = ""
        while remaining_reading_content_percentage > 0 and \
                self.get_element_location_window_offset(html_web_element).get("bottom") > \
                browser_inner_size.get("height"):
            if remaining_reading_content_percentage < 50 and rand.random() < 0.08:
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> Current Activity --> Scrolling To Random Point On Article")
                random_max = 100 - remaining_reading_content_percentage
                self.scroll_to_percentage_in_element(
                    html_web_element, rand.uniform(1, random_max), rand.uniform(0.9, 2))

            # Release Mouse Hold If Mode In Last Read Was Mouse To ScrollBar
            if mode == "mouse_to_scrollbar":
                pyautogui.mouseUp()
                WebBot.active_on_mouse_movement.value = -self.bot_process_id if self.bot_process_id != 0 else -500

            mode = "arrow_keys"
            if isinstance(self.touch, Touchscreen):
                mode = "touch"
            elif isinstance(self.mouse, Mouse):
                mode = "wheel"
                if rand.random() < bot_constants.USE_MOUSE_READ_PROBABILITY and WebBot.active_on_mouse_movement.value < 0:
                    WebBot.active_on_mouse_movement.value = self.bot_process_id
                    mode = "mouse_to_scrollbar"
                    self.bring_window_to_front()
            elif rand.random() < bot_constants.USE_MOUSE_READ_PROBABILITY and WebBot.active_on_mouse_movement.value < 0:
                WebBot.active_on_mouse_movement.value = self.bot_process_id
                mode = "mouse_to_scrollbar"
                self.bring_window_to_front()

            if remaining_reading_content_percentage < 26:
                next_read_sequence_percentage = remaining_reading_content_percentage
                remaining_reading_content_percentage = 0
            else:
                next_read_sequence_percentage = rand.randint(25, remaining_reading_content_percentage)
                remaining_reading_content_percentage -= next_read_sequence_percentage

            next_read_sequence_time = utils.fetch_percentage_value(
                seconds_to_read, next_read_sequence_percentage + rand.uniform(-1.2, 1.2))

            # There are possiblities next_read_sequence_time could be less than zero, resetting
            if next_read_sequence_time < 0:
                next_read_sequence_time = 0

            print(f"Bot Process Id {self.bot_process_id} <:::> Navigation Mode -->", mode)
            print(f"Bot Process Id {self.bot_process_id} <:::> Remaining Content Percentage To Read -->",
                  remaining_reading_content_percentage)

            if read(next_read_sequence_time, html_web_element, mode, next_read_sequence_percentage) == "ad_clicked":
                print(
                    f"BOT PROCESS ID {self.bot_process_id} <:::> AD WAS CLICKED, STOPPED READING ARTICLE")
                return "ad_clicked"
        if mode == "mouse_to_scrollbar":
            pyautogui.mouseUp()
            WebBot.active_on_mouse_movement.value = -self.bot_process_id if self.bot_process_id != 0 else -500
        print(
            f"ARTICLE READ SESSION COMPLETED, BOT THREAD ID {self.bot_process_id} | TIME SPENT: {time.time() - time_started}")
        return True

    def bring_window_to_front(self):
        self.web_browser_driver.switch_to.window(self.web_browser_driver.current_window_handle)

    def move_mouse_to_fool_exit_point(self):
        """
        Attempts to move mouse towards the browser exit button
        :return: Boolean
        """
        if WebBot.active_on_mouse_movement.value < 0:
            WebBot.active_on_mouse_movement.value = self.bot_process_id
            self.bring_window_to_front()
            self.simulate_human_mouse_move_behavior_to_point(rand.randint(0, bot_constants.SCREEN_WIDTH), 4)
            time.sleep(0.5)
            WebBot.active_on_mouse_movement.value = -self.bot_process_id if self.bot_process_id != 0 else -500
            return True
        return False

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

    def move_pointing_device_to_element(self, html_web_element: remote_webdriver.WebElement,
                                        simulate_human_behaviour=True):
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

                self.simulate_human_mouse_move_behavior_to_area(el_pos["area_x"] + 1, el_pos["area_y"] + 1,
                                                                el_pos["area_width"] - 2, el_pos["area_height"] - 2,
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

    def track_request_size(self, request):
        print(f"Request url: {request.url}[{request.method}]")
        request_size = len(request.body or '') / 1024
        self.total_request_size += request_size

    def track_response_size(self, request, response):
        print(f"Response url: {request.url}[{response.status_code}]")
        if request.url in self.urls_through_proxy:
            self.url_through_proxy_response_size += len(response.body or '') / 1024
            self.urls_through_proxy.remove(request.url)
        elif request.url not in self.urls_cached:
            self.uncached_response_size += len(response.body or '') / 1024
        else:
            print(f'Bot Process Id {self.bot_process_id} <:::> {request.url} is cached')
            self.urls_cached.remove(request.url)
            self.cached_response_size += len(response.body or '') / 1024

    def print_total_usage(self):
        print(f'Bot Process Id {self.bot_process_id} <:::> Total request size: {self.total_request_size:.2f} KB')
        print(
            f'Bot Process Id {self.bot_process_id} <:::> Total uncached response size: {self.uncached_response_size:.2f} KB')
        print(
            f'Bot Process Id {self.bot_process_id} <:::> Total proxy response size: {self.url_through_proxy_response_size:.2f} KB')
        print(
            f'Bot Process Id {self.bot_process_id} <:::> Total cached response size: {self.cached_response_size:.2f} KB')
        print(f'Bot Process Id {self.bot_process_id} <:::> Total data transferred: '
              f'{self.total_request_size + self.uncached_response_size + self.url_through_proxy_response_size:.2f} KB')

    def response_interceptor(self, request: request.Request, response: request.Response):
        if self.terminate_unecessary_redirects(request, response):
            return
        self.track_response_size(request, response)
        self.print_total_usage()

        self.inject_js_to_spoof_fingerprintable_objects_on_website_server_response(request, response)

    def terminate_unecessary_requests(self, request):
        if request.url.endswith((".crx", "crx3")):
            request.abort()
            return True
        return False

    def terminate_unecessary_redirects(self, request, response):
        to_terminate_by_host = ["rndhaunteran.com", "woafoame.net", "twnt1.rdtk.io"]
        if any(host in request.url for host in to_terminate_by_host) and response.status_code in [301, 302]:
            request.abort()
            return True

    def request_interceptor(self, request: request.Request):
        if self.terminate_unecessary_requests(request):
            return

        def network_through_no_proxy():
            try:
                response = self.cached_requests_session.request(url=request.url, verify=False, headers=request.headers,
                                                                allow_redirects=False, method=request.method,
                                                                data=request.body)
                if response.from_cache:
                    self.urls_cached.add(request.url)
            except SSLError:
                print(
                    f'Bot Process Id {self.bot_process_id} <:::> {request.url} would not be able to go through the cacher as a result of an ssl error')
                return

        def network_through_proxy():
            print(f'Bot Process Id {self.bot_process_id} <:::> {request.url} is passing through the proxy')
            try:
                response = self.requests_session.request(url=request.url, verify=False, headers=request.headers,
                                                         allow_redirects=False, method=request.method,
                                                         data=request.body)
            except (SSLError, ProxyError):
                print(
                    f'Bot Process Id {self.bot_process_id} <:::> {request.url} generated an ssl or proxy error, it won\'t go through proxy')
                return

            self.urls_through_proxy.add(request.url)
            response.body = response.content
            request.response = response

        self.track_request_size(request)
        self.print_total_usage()
        self.inject_referer_into_header(request)
        if bot_constants.PROXY_WHITELISTED_DOMAINS == "*":
            if utils.url_ends_with(request.url, bot_constants.PROXY_BLACKLISTED_EXTENSIONS) or \
                    utils.has_string_in(request.host, bot_constants.PROXY_BLACKLISTED_DOMAINS):
                network_through_no_proxy()
            else:
                network_through_proxy()
        # fetching driver.current_url while a page is loading posed some issues, you can find alternate ways to implement the check of if current url equates browser active loading url
        elif not ((utils.has_string_in(request.host, bot_constants.PROXY_WHITELISTED_DOMAINS) and not utils
                .url_ends_with(request.url, bot_constants.PROXY_BLACKLISTED_EXTENSIONS)) and not utils.has_string_in(
            request.host, bot_constants.PROXY_BLACKLISTED_DOMAINS)):
            network_through_no_proxy()
        else:
            network_through_proxy()

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
                            webgl_params=(
                                self.identity.gpu_vendor, 15, 12, 14, 14, 13, 4, 4, 4, 4, 3, 3, 3, 3, 6, 11, 12, 12,
                                self.identity.gpu_renderer), timezone=self.identity.timezone,
                            font_width_offset=self.identity.font_fp_offset[0],
                            font_height_offset=self.identity.font_fp_offset[1],
                            platform=self.identity.platform,
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
                            body = body.encode('utf-8')
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
                print(f"Identity: {self.identity.id} On Process: {self.bot_process_id} Could Not Perform "
                      f"Activity Within Set Time, Exiting Session...")
                try:
                    if self.web_browser_driver.session_id:
                        print(f"Bot Process Id {self.bot_process_id} <:::> Updating Cookies To Cloud")
                        self.release_proxies()
                        self.update_cookies_to_cloud()
                        self.web_browser_driver.quit()
                except ConnectionRefusedError:
                    print(
                        "A connection refused error occurred, this would likely be as a result of a dead browser session")
            else:
                self.quit_browser_after_max_alive(sleep_time=5)

    @staticmethod
    def _handle_prefs(options):
        if prefs := options.experimental_options.get("prefs"):
            # turn a (dotted key, value) into a proper nested dict
            def undot_key(key, value):
                if "." in key:
                    key, rest = key.split(".", 1)
                    value = undot_key(rest, value)
                return {key: value}

            # undot prefs dict keys
            undot_prefs = reduce(
                lambda d1, d2: {**d1, **d2},  # merge dicts
                (undot_key(key, value) for key, value in prefs.items()),
            )

            # create an user_data_dir and add its path to the options
            user_data_dir = os.path.normpath(tempfile.mkdtemp())
            options.add_argument(f"--user-data-dir={user_data_dir}")

            # create the preferences json file in its default directory
            default_dir = os.path.join(user_data_dir, "Default")
            os.mkdir(default_dir)

            prefs_file = os.path.join(default_dir, "Preferences")
            with open(prefs_file, encoding="latin1", mode="w") as f:
                json.dump(undot_prefs, f)

            # pylint: disable=protected-access
            # remove the experimental_options to avoid an error
            del options._experimental_options["prefs"]

    def open_web_browser(self, use_proxy=False):
        open_browser_in_full_screen = True
        window_size = (bot_constants.SCREEN_WIDTH, bot_constants.SCREEN_HEIGHT)
        # An 8% chance and device is pc that randomly resize the web browser in a manner that is unobstructive
        if rand.random() < 0.08 and self.identity.device_type == "is_pc":
            open_browser_in_full_screen = False
            window_size = utils.fetch_random_window_size_relative_to_screen(
                bot_constants.SCREEN_WIDTH, bot_constants.SCREEN_HEIGHT)
        # Opens a chrome browser
        if self.browser_to_use_id == browser_constants.CHROME_ID:
            print(f"Bot Process Id {self.bot_process_id} <:::> Opening Chrome Browser")
            browser_options = webdriver.ChromeOptions()
            # browser_options.add_argument(f'--disk-cache-dir={bot_constants.FULL_DIRECTORY_PATH}/chrome_cache')
            browser_options.add_argument('--disable-background-networking')
            browser_options.add_argument('--disable-background-timer-throttling')
            browser_options.add_argument('--disable-backgrounding-occluded-windows')
            browser_options.add_argument('--enable-logging=0')
            browser_options.add_argument('--disable-remote-fonts')
            browser_options.add_argument("--disable-extensions")
            browser_options.add_argument('--disable-gpu')
            browser_options.add_experimental_option('prefs',
                                                    {'intl.accept_languages': ','.join(self.identity.languages)})
            self._handle_prefs(browser_options)
            # browser_options.add_argument('--disable-dev-shm-usage')
            # browser_options.add_argument('--disable-setuid-sandbox')
            # browser_options.add_argument('--no-sandbox')
            # browser_options.add_argument('--dns-prefetch-disable')
            # browser_options.add_argument('--blink-settings=imagesEnabled=false')
            # browser_options.add_argument('--disable-plugin-discovery')
            if self.identity.user_agent:
                browser_options.add_argument(f"--user-agent={self.identity.user_agent}")
            browser_options.binary_location = browser_constants.CHROME_BINARY_LOCATION
            if open_browser_in_full_screen:
                browser_options.add_argument("--start-maximized")
            else:
                browser_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
            sw_options = {
            }
            self.web_browser_driver = sw_uc.Chrome(
                driver_executable_path=self.driver_path, options=browser_options, seleniumwire_options=sw_options)

            # Opens a firefox browser
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
        # If device to emulate is a smartphone, set chrome to mobile mode
        if self.identity.device_type == "is_smartphone":
            print(f"Bot Process Id {self.bot_process_id} <:::> Device Name:", self.identity.hardware)
            self.activate_mobile()
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Page To Always Be In Focus")
        # Sets Browser to always be active
        devtools_primary.activate_all_focus(self.web_browser_driver)
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Cookies From Identity")
        # Delete existing cookies
        devtools_primary.clear_all_cookies(self.web_browser_driver)
        # Sets cookies from identity
        devtools_primary.set_all_cookies(self.web_browser_driver, self.identity.cookies)
        # If identity has a user agent, change browser user agent to identity's
        if self.identity.user_agent:
            print(
                f"Bot Process Id {self.bot_process_id} <:::> Setting User Agent: {self.identity.user_agent} From Identity")
            devtools_primary.change_user_agent(
                self.web_browser_driver,
                self.identity.user_agent, self.identity.platform)
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Timezone From Identity")
        # Set Timezone
        devtools_primary.set_timezone(self.web_browser_driver, self.identity.timezone[0])
        self.browser_action_chains = ActionChains(self.web_browser_driver)
        self.keyboard = Keyboard(self.web_browser_driver)
        if self.identity.has_touch == "has_touch":
            self.touch = Touchscreen(self.web_browser_driver, self.keyboard)
        self.web_browser_driver.implicitly_wait(bot_constants.IMPLICITLY_WAIT_TIME)
        # self.web_browser_driver.set_window_position(0, 0)
        if open_browser_in_full_screen:
            self.web_browser_driver.maximize_window()
        else:
            self.web_browser_driver.set_window_position(0, 0)
            self.web_browser_driver.set_window_size(*window_size)
        self.web_browser_driver.request_interceptor = self.request_interceptor
        self.web_browser_driver.response_interceptor = \
            self.response_interceptor
        t = Thread(target=self.quit_browser_after_max_alive)
        t.daemon = True
        t.start()
        if use_proxy:
            proxy_path = self.identity.proxy_url
            self.proxy = {
                'http': 'http://' + proxy_path,
                'https': 'http://' + proxy_path,
                'no_proxy': 'localhost,127.0.0.1'
            }
            print(f"Bot Process Id {self.bot_process_id} <:::> Adding a proxy option for this session on this proxy"
                  f" path: {proxy_path}")
            self.requests_session.proxies = self.proxy

    def wait_for_element_visible(self, locator):
        """
        Waits for an element to be visible on the page
        :param locator: tuple of (By, locator) used to identify the element
        :return: the WebElement when it is visible
        """
        wait = WebDriverWait(self.web_browser_driver, 10)
        return wait.until(EC.visibility_of_element_located(locator))

    def revert_to_main_page(self, recurse=False, time_interval_to_check=0.4):
        """
        Returns page to main if changed
        :param time_interval_to_check: number of seconds to wait for before checking, set to zero if wanted instantly
        :return: True if page changed, else false
        """
        time.sleep(time_interval_to_check)
        # Switch to the new window and capture its handle
        if self.current_tab_length != len(self.web_browser_driver.window_handles):
            self.web_browser_driver.switch_to.window(self.web_browser_driver.current_window_handle)
            self.current_tab_length = len(self.web_browser_driver.window_handles)
            if recurse:
                self.revert_to_main_page(recurse, time_interval_to_check)
            return True
        if recurse:
            self.revert_to_main_page(recurse, time_interval_to_check)
        return False

    def activate_mobile(self):
        devtools_primary.activate_mobile(self.web_browser_driver,
                                         {"width": self.identity.screen_width,
                                          "height": self.identity.screen_height, "deviceScaleFactor":
                                              self.identity.screen_resolution[4], "screenOrientation":
                                              {"type": "portraitPrimary", "angle": 0},
                                          "mobile": True})

    def revert_to_main_page_if_ever_changed(self):
        """
        Create Thread object to constantly check if page changed
        :return: Thread object
        """
        t = Thread(target=self.revert_to_main_page, args=(True,))
        t.daemon = True
        return t.start()

    def close_ad(self):
        pass

    def fetch_all_cookies(self):
        return devtools_primary.get_all_cookies(self.web_browser_driver)

    def set_all_cookies(self, cookies):
        devtools_primary.set_all_cookies(cookies)
        return True

    def release_proxies(self):
        # release proxyrack sticky session
        if self.identity.proxy_client == "proxyrack.com":
            print(f"Bot Process Id {self.bot_process_id} <:::> Releasing proxyrack proxy session")
            try:
                print(
                    main_requests.request(url="http://api.proxyrack.net/release", method="GET", proxies=self.proxy).json())
            except:
                print(f"Bot Process Id {self.bot_process_id} <:::> An error occurred proxyrack proxy session")

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
                        print(
                            f"Bot Process Id {self.bot_process_id} <:::> Unable To Open Url: " + url + ", With Name: " + url_name)
                    return True
        elif force_browser_diversion:
            """Create A Method That Checks All Other Opened Browsers To 
        Open The Url Incase Chrome Isn't Alive"""
        else:
            raise NameError("No Available Chrome Browser, Either Set One Up by Using The "
                            "'open_web_browser_driver' or Force Browser Diversion")
        return False

    def __exit__(self):
        print(f"Bot Process Id {self.bot_process_id} <:::> Cookies: ",
              devtools_primary.get_all_cookies(self.web_browser_driver))
