import random
import time
import asyncio

import pyautogui
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    InvalidArgumentException,
)
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By

from bots import utils
from browsers.browser_interface import BrowserInterface
from humanbehaviourmechanics.human_movements import HumanMovements


class SmartAdsInteractions:
    def __init__(
        self,
        no_of_clicks=0,
    ):
        self.ad_with_keyword_wait_counter = 0

        self.probability_of_click = 0.45
        self.ad_to_click = False

        self.vignette_ad_close_type = None
        self.vignette_ad_close_name = None
        self.vignette_ad_open_type = None
        self.vignette_ad_open_name = None

        self.in_page_ad_links_type = None
        self.in_page_ad_links_name = None

        self.ad_keywords = None
        self.ad_negative_keywords = None

    async def strip_ads_with_negative_keywords(self, ads_dimensions):
        if isinstance(self.ad_negative_keywords, list):
            for index, ad_dimensions in enumerate(ads_dimensions):
                for keyword in self.ad_negative_keywords:
                    if keyword in ad_dimensions["text_content"]:
                        ads_dimensions.pop(index)
            if len(ads_dimensions == 0):
                return False

    async def trigger_vignette(self, open_vignette=False):
        try:
            if not open_vignette:
                ads_dimensions = await self.locate_ad_elements_in_iframe(
                    ads_elements_type=self.vignette_ad_close_type,
                    ads_elements_name=self.vignette_ad_close_name,
                )
            else:
                ads_dimensions = await self.locate_ad_elements_in_iframe(
                    ads_elements_type=self.vignette_ad_open_type,
                    ads_elements_name=self.vignette_ad_open_name,
                )
                if self.strip_ads_with_negative_keywords(ads_dimensions):
                    return False
            if not ads_dimensions:
                return
            await asyncio.sleep(0.5)
            if not open_vignette:
                self.ad_click(random.choice(ads_dimensions), revert_back=False)
            else:
                self.ad_click(random.choice(ads_dimensions))
            print(
                f"Bot Process Id {self.bot_process_id} <:::> Vignette ad trigger attempted"
            )
            await asyncio.sleep(0.5)
            self.trigger_vignette()
        except TimeoutException:
            # I no longer use Expected conditions in the iframe_check for locating elements, so this branch of code may
            # never be reached, look for other ways
            print(
                f"Bot Process Id {self.bot_process_id} <:::> No active vignette to close"
            )
            return

    async def smart_ad_click(self, switch_focus_to_new_tab=True):
        ad_click_success = False
        if not hasattr(self, "track_vignette_close"):
            self.track_vignette_close = 1
        # Smart reader calls this function after each read loop, and searching for elements is expensive, hence this
        if (
            self.ad_to_click != "vignette"
            and self.vignette_ad_close_name
            and self.track_vignette_close >= 3
        ):
            self.trigger_vignette()
            self.track_vignette_close = 0
        else:
            self.track_vignette_close += 1
        tab_length = len(self.web_browser_driver.window_handles)
        try:
            if self.ad_to_click == "vignette" and self.vignette_ad_open_name:
                # Resetting time activated before loading, so ad page has more time to load
                self.time_activated = time.time()
                # This creates a possibility where the ad will be closed before eventually getting triggered. If
                # migrating to adsense, you probably want to recheck
                if random.random() < 0.03:
                    self.trigger_vignette()
                    return
                self.trigger_vignette(open_vignette=True)
                if tab_length != len(self.web_browser_driver.window_handles):
                    self.ad_to_click = None
                    ad_click_success = True
                else:  # the reason why this condition branch was added was because of the possibility trigger_vignette
                    # might not trigger, most likely because ad contained negative keywords
                    self.trigger_vignette()
            elif self.ad_to_click == "in_page" and self.in_page_ad_links_name:
                self.trigger_vignette()
                await asyncio.sleep(0.4)
                ads_dimensions = self.locate_ad_elements_in_iframe(
                    ads_elements_type=self.in_page_ad_links_type,
                    ads_elements_name=self.in_page_ad_links_name,
                )
                if not ads_dimensions:
                    return

                if (
                    not isinstance(self.ad_keywords, list)
                    or self.ad_with_keyword_wait_counter >= 1
                ):
                    print(
                        f"Bot Process Id {self.bot_process_id} <:::> Keywords won't be used as basis for ad click"
                    )
                    # Resetting time activated before loading, so ad page has more time to load
                    self.time_activated = time.time()
                    if self.ad_click(
                        random.choice(ads_dimensions)
                    ) and tab_length != len(self.web_browser_driver.window_handles):
                        ad_click_success = True
                        self.ad_to_click = None
                else:
                    for ad_dimensions in ads_dimensions:
                        for keyword in self.ad_keywords:
                            if keyword in ad_dimensions["text_content"]:
                                # Resetting time activated before loading, so ad page has more time to load
                                self.time_activated = time.time()
                                if self.ad_click(ad_dimensions) and tab_length != len(
                                    self.web_browser_driver.window_handles
                                ):
                                    ad_click_success = True
                                    self.ad_to_click = None
                                print(
                                    f"Bot Process Id {self.bot_process_id} <:::> Keyword was used as a base to click "
                                    f"an ad"
                                )
                                break
                        else:
                            continue
                        break
                    if self.ad_to_click:
                        self.ad_with_keyword_wait_counter += 1
                        print(
                            f"Bot Process Id {self.bot_process_id} <:::> Ad with any of keywords wasn't found, "
                            f"Try again"
                        )
            if ad_click_success and switch_focus_to_new_tab:
                await asyncio.sleep(1)
                self.web_browser_driver.switch_to.window(
                    self.web_browser_driver.window_handles[-1]
                )
            if self.device_type == "is_smartphone":
                self.activate_mobile()
            return ad_click_success
        except TimeoutException:
            print(f"Bot Process Id {self.bot_process_id} <:::> No ads found, Try again")

    async def locate_ad_elements_in_iframe(
        self, ads_elements_type, ads_elements_name: str
    ):
        async def iframe_check():
            try:
                iframe = self.web_browser_driver.main_tab.query_selector("iframe")
                if self.device_type == "is_smartphone":
                    iframe_offset = self.get_element_location_window_offset(iframe)
                else:
                    iframe_offset = self.get_element_window_location_screen_offsets(
                        iframe
                    )["html_web_element"]
                self.web_browser_driver.switch_to.frame(iframe)
            except (WebDriverException, StaleElementReferenceException):
                self.web_browser_driver.switch_to.default_content()
                return False
            ads_elements = None
            try:
                ads_elements = self.web_browser_driver.find_elements(
                    ads_elements_type, ads_elements_name
                )
            except (TimeoutException, InvalidArgumentException):
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> Element parent body was found but ad elements to "
                    f"interact with were not present"
                )
                self.web_browser_driver.switch_to.default_content()
            if not ads_elements:
                self.web_browser_driver.switch_to.default_content()
                return
            ads_elements_rect = []
            for ad_element in ads_elements:
                rect = ad_element.rect.copy()
                if self.device_type == "is_smartphone":
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
            print(
                f"Bot Process Id {self.bot_process_id} <:::> The ads type you are trying to locate is not supported"
            )
            return
        if ads_elements_name.startswith("//iframe"):
            ads_elements_name = ads_elements_name[8:]
            return iframe_check()

    async def set_ad_behaviour_environment(
        self,
        ad_to_click,
        vignette_ad_close_type,
        vignette_ad_close_name,
        vignette_ad_open_type,
        vignette_ad_open_name,
        in_page_ad_links_type,
        in_page_ad_links_name,
        ad_keywords=None,
    ):
        self.ad_to_click = ad_to_click

        self.vignette_ad_close_type = vignette_ad_close_type
        self.vignette_ad_close_name = vignette_ad_close_name
        self.vignette_ad_open_type = vignette_ad_open_type
        self.vignette_ad_open_name = vignette_ad_open_name

        self.in_page_ad_links_type = in_page_ad_links_type
        self.in_page_ad_links_name = in_page_ad_links_name
        self.ad_keywords = ad_keywords

    async def close_ad(self):
        pass

    async def ad_click(self, ad_dimensions: dict, revert_back=False):
        if self.device_type == "is_pc":
            previous_mouse_pos = pyautogui.position()
            self.simulate_human_mouse_move_behavior_to_area(
                ad_dimensions["x"],
                ad_dimensions["y"],
                ad_dimensions["width"],
                ad_dimensions["height"],
                x_coordinates_offset_percentage=random.randint(0, 100),
                y_coordinates_offset_percentage=random.randint(0, 100),
                max_overshoot=35,
                probability_of_overshoot=round(random.random(), 2),
            )
            await asyncio.sleep(random.uniform(0.1, 0.4))
            pyautogui.click()
            if revert_back:
                self.revert_to_main_page()
            self.simulate_human_mouse_move_behavior_to_point(
                previous_mouse_pos[0], previous_mouse_pos[1]
            )
            return True
        elif self.device_type == "is_smartphone":
            self.touch.tap(
                ad_dimensions["x"] + random.uniform(0, ad_dimensions["width"]),
                ad_dimensions["y"] + random.uniform(0, ad_dimensions["height"]),
            )
            if revert_back:
                self.revert_to_main_page()
            return True
