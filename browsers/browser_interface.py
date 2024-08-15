import json
import os
import random
import time
import tempfile
from functools import reduce
from selenium.webdriver import ActionChains
from threading import Thread

from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common import NoAlertPresentException
import seleniumwire.undetected_chromedriver.v2 as sw_uc
from seleniumwire import webdriver

from bots import utils
from bots.devtools import devtools_primary
from constants import bot_constants, browser_constants, config


class BrowserInterface:
    def __init__(self, browser_to_use_id=browser_constants.CHROME_ID,
                 bot_process_id=None, timezone_id=None, device_type="is_pc",
                 has_touch="no_touch", has_mouse="no_mouse", languages=["en-US", "en"], user_agent=None, hardware=None,
                 platform={}, screen_width=1920, screen_height=1080, device_pixel_ratio=1, cookies=list(),
                 identity_id=None, cookies_update_callback=None):
        self.web_browser_driver = None
        self.time_activated = time.time()
        self.browser_to_use_id = browser_to_use_id
        self.opened_browser_urls = dict()
        self.bot_process_id = bot_process_id
        self.current_tab_length = 1
        self.timezone_id = timezone_id
        self.device_type = device_type
        self.has_touch = has_touch
        self.has_mouse = has_mouse
        self.languages = languages
        self.user_agent = user_agent
        self.hardware = hardware
        self.platform = platform
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.device_pixel_ratio = device_pixel_ratio
        self.cookies = cookies
        self.cookies_update_callback = cookies_update_callback
        self.identity_id = identity_id
        self.browser_action_chains = None

    def wait_for_element_visible(self, locator):
        """
        Waits for an element to be visible on the page
        :param locator: tuple of (By, locator) used to identify the element
        :return: the WebElement when it is visible
        """
        wait = WebDriverWait(self.web_browser_driver, 10)
        return wait.until(EC.visibility_of_element_located(locator))

    def resolve_active_alert(self):
        try:
            alert = self.web_browser_driver.switch_to.alert
            alert.accept()
        except NoAlertPresentException:
            pass

    def update_cookies_to_cloud(self):
        self.resolve_active_alert()
        if self.cookies_update_callback:
            return self.cookies_update_callback(self.fetch_all_cookies())
            # self.identity.update_cookies() put in the callback
        else:
            return self.fetch_all_cookies()

    def open_new_tab(self, url):
        """
        param url: Url Location Of The WebPage
        return: Return True On Success
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

    def get_element_window_location_screen_offsets(self, html_web_element: WebElement):
        """
        Calculate And Return Both Window And Element Location Offsets Relative To Screen
        :param html_web_element: Target HTML Element
        :return: Offset Locations Of Element(tuple) And Browser(tuple) In a Dict()
        """
        # Getting HTML Web Element Coordinates Which Are Relative From The Window Point And Dimensions
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

    def get_element_location_window_offset(self, html_web_element: WebElement):
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

    def get_window_document_offsets(self):
        return {"y_offset": self.web_browser_driver.execute_script("return window.pageYOffset"),
                "x_offset": self.web_browser_driver.execute_script("return window.pageXOffset")}

    def bring_window_to_front(self):
        self.web_browser_driver.switch_to.window(self.web_browser_driver.current_window_handle)

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
                                         {"width": self.screen_width,
                                          "height": self.screen_height, "deviceScaleFactor":
                                              self.device_pixel_ratio, "screenOrientation":
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

    def fetch_all_cookies(self):
        return devtools_primary.get_all_cookies(self.web_browser_driver)

    def quit_browser_after_max_alive(self, sleep_time=bot_constants.BOT_MIN_ALIVE_TIME):
        time.sleep(sleep_time)
        if hasattr(self, "web_browser_driver"):
            if time.time() - self.time_activated > bot_constants.BOT_MAX_ALIVE_TIME + random.uniform(-6.5, 6.5):
                print(f"Identity: {self.identity_id} On Process: {self.bot_process_id} Could Not Perform "
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
            def un_dot_key(key, value):
                if "." in key:
                    key, rest = key.split(".", 1)
                    value = un_dot_key(rest, value)
                return {key: value}

            # un-dot prefs dict keys
            un_dot_prefs = reduce(
                lambda d1, d2: {**d1, **d2},  # merge dicts
                (un_dot_key(key, value) for key, value in prefs.items()),
            )

            # create a user_data_dir and add its path to the options
            user_data_dir = os.path.normpath(tempfile.mkdtemp())
            options.add_argument(f"--user-data-dir={user_data_dir}")

            # create the preferences json file in its default directory
            default_dir = os.path.join(user_data_dir, "Default")
            os.mkdir(default_dir)

            prefs_file = os.path.join(default_dir, "Preferences")
            with open(prefs_file, encoding="latin1", mode="w") as f:
                json.dump(un_dot_prefs, f)

            # pylint: disable=protected-access
            # remove the experimental_options to avoid an error
            del options._experimental_options["prefs"]

    def open_web_browser(self):
        open_browser_in_full_screen = True
        window_size = (bot_constants.SCREEN_WIDTH, bot_constants.SCREEN_HEIGHT)
        # An 8% chance and device is pc that randomly resize the web browser in a manner that is un-obstructive
        if random.random() >= browser_constants.MAXIMUM_WINDOW_PROBABILITY and self.device_type == "computer":
            open_browser_in_full_screen = False
            window_size = utils.fetch_random_window_size_relative_to_screen(
                bot_constants.SCREEN_WIDTH, bot_constants.SCREEN_HEIGHT)
        # Opens a Chrome browser
        if self.browser_to_use_id == browser_constants.CHROME_ID:
            print(f"Bot Process Id {self.bot_process_id} <:::> Opening Chrome Browser")
            browser_options = webdriver.ChromeOptions()
            browser_options.add_argument('--disable-background-networking')
            browser_options.add_argument('--disable-background-timer-throttling')
            browser_options.add_argument('--disable-backgrounding-occluded-windows')
            browser_options.add_argument('--enable-logging=0')
            browser_options.add_argument('--disable-remote-fonts')
            browser_options.add_argument("--disable-extensions")
            browser_options.add_argument('--disable-gpu')
            browser_options.add_experimental_option('prefs',
                                                    {'intl.accept_languages': ','.join(self.languages)})
            if browser_constants.IGNORE_SSL:
                browser_options.add_argument('--ignore-certificate-errors')
            if config.CONTAINERIZED:
                browser_options.add_argument('--no-sandbox')
            self._handle_prefs(browser_options)
            if self.user_agent:
                browser_options.add_argument(f"--user-agent={self.user_agent}")
            browser_options.binary_location = browser_constants.CHROME_BINARY_LOCATION
            if open_browser_in_full_screen:
                if random.random() <= browser_constants.KIOSK_MODE_PROBABILITY:
                    browser_options.add_argument("--kiosk")
                else:
                    browser_options.add_argument("--start-maximized")
            else:
                browser_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
            sw_options = {
            }
            browser_options.binary_location = bot_constants.FULL_DIRECTORY_PATH+browser_constants.CHROME_BINARY_LOCATION
            self.web_browser_driver = sw_uc.Chrome(
                driver_executable_path=bot_constants.FULL_DIRECTORY_PATH+bot_constants.CHROME_WEBDRIVER_LOCATION,
                options=browser_options, seleniumwire_options=sw_options)

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
        if self.device_type == "is_smartphone":
            print(f"Bot Process Id {self.bot_process_id} <:::> Device Name:", self.hardware)
            self.activate_mobile()
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Page To Always Be In Focus")
        # Sets Browser to always be active
        # devtools_primary.activate_all_focus(self.web_browser_driver)
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Cookies From Identity")
        # Delete existing cookies
        devtools_primary.clear_all_cookies(self.web_browser_driver)
        # Sets cookies from identity
        devtools_primary.set_all_cookies(self.web_browser_driver, self.cookies)
        # If identity has a user agent, change browser user agent to identity's
        if self.user_agent:
            print(
                f"Bot Process Id {self.bot_process_id} <:::> Setting User Agent: {self.user_agent} From Identity")
            devtools_primary.change_user_agent(
                self.web_browser_driver,
                self.user_agent, self.platform)
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Timezone From Identity")
        # Set Timezone
        devtools_primary.set_timezone(self.web_browser_driver, self.timezone_id)
        self.web_browser_driver.implicitly_wait(bot_constants.IMPLICITLY_WAIT_TIME)
        # self.web_browser_driver.set_window_position(0, 0)
        if not open_browser_in_full_screen:
            self.web_browser_driver.set_window_position(0, 0)
            self.web_browser_driver.set_window_size(*window_size)

        self.web_browser_driver.request_interceptor = self.request_interceptor
        self.web_browser_driver.response_interceptor = self.response_interceptor
        self.browser_action_chains = ActionChains(self.web_browser_driver)
        t = Thread(target=self.quit_browser_after_max_alive)
        t.daemon = True
        t.start()
