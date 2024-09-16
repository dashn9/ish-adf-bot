import random
import time
import asyncio

import pyautogui


class SmartAdsInteractions:
    def __init__(
        self,
        no_of_clicks=0,
    ):
        self.ad_with_keyword_wait_counter = 0

        self.probability_of_click = 0.45
        self.ad_to_click = False

        self.vignette_ad_close = None
        self.vignette_ad_open = None

        self.in_page_ad_links_open = None

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
        if not open_vignette:
            ads_dimensions = await self.locate_ad_elements_in_iframe(
                ads_elements_selector=self.vignette_ad_close,
            )
        else:
            ads_dimensions = await self.locate_ad_elements_in_iframe(
                ads_elements_selector=self.vignette_ad_open,
            )
            if await self.strip_ads_with_negative_keywords(ads_dimensions):
                return False
        if not ads_dimensions:
            return
        await asyncio.sleep(0.5)
        if not open_vignette:
            await self.ad_click(random.choice(ads_dimensions), revert_back=False)
        else:
            await self.ad_click(random.choice(ads_dimensions))
        print(
            f"Bot Process Id {self.bot_process_id} <:::> Vignette ad trigger attempted"
        )
        await asyncio.sleep(0.5)
        await self.trigger_vignette()
        # I no longer use Expected conditions in the iframe_check for locating elements, so this branch of code may
        # never be reached, look for other ways
        # print(
        #     f"Bot Process Id {self.bot_process_id} <:::> No active vignette to close"
        # )
        return

    async def smart_ad_click(self, switch_focus_to_new_tab=True):
        ad_click_success = False
        if not hasattr(self, "track_vignette_close"):
            self.track_vignette_close = 1
        # Smart reader calls this function after each read loop, and searching for elements is expensive, hence this
        # Seperate the The count before checking into config, i reduced it to 1, because I can now afford it as i'm running a cluster now :-)
        if (
            self.ad_to_click != "vignette"
            and self.vignette_ad_close
            and self.track_vignette_close >= 1
        ):
            await self.trigger_vignette()
            self.track_vignette_close = 0
        else:
            self.track_vignette_close += 1
        tab_length = len(self.web_browser_driver.tabs)
        if self.ad_to_click == "vignette" and self.vignette_ad_open:
            # Resetting time activated before loading, so ad page has more time to load
            self.time_activated = time.time()
            # This creates a possibility where the ad will be closed before eventually getting triggered. If
            # migrating to adsense, you probably want to recheck
            if random.random() < 0.03:
                await self.trigger_vignette()
                return
            await self.trigger_vignette(open_vignette=True)
            if tab_length != len(self.web_browser_driver.tabs):
                self.ad_to_click = None
                ad_click_success = True
            else:  # the reason why this condition branch was added was because of the possibility trigger_vignette
                # might not trigger, most likely because ad contained negative keywords
                await self.trigger_vignette()
        elif self.ad_to_click == "in_page" and self.in_page_ad_links_open:
            await self.trigger_vignette()
            await asyncio.sleep(0.4)
            ads_dimensions = await self.locate_ad_elements_in_iframe(
                ads_elements_selector=self.in_page_ad_links_open,
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
                if await self.ad_click(
                    random.choice(ads_dimensions)
                ) and tab_length != len(self.web_browser_driver.tabs):
                    ad_click_success = True
                    self.ad_to_click = None
            else:
                for ad_dimensions in ads_dimensions:
                    for keyword in self.ad_keywords:
                        if keyword in ad_dimensions["text_content"]:
                            # Resetting time activated before loading, so ad page has more time to load
                            self.time_activated = time.time()
                            if await self.ad_click(ad_dimensions) and tab_length != len(
                                self.web_browser_driver.tabs
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
            self.web_browser_driver.switch_to.window(self.web_browser_driver.tabs[-1])
        if self.device_type == "smartphone":
            self.activate_mobile()
        return ad_click_success
        # print(f"Bot Process Id {self.bot_process_id} <:::> No ads found, Try again")

    async def locate_ad_elements_in_iframe(self, ads_elements_selector):
        async def iframe_check():
            iframe = await self.web_browser_driver.main_tab.select("iframe")
            if not iframe:
                return
            if self.device_type == "smartphone":
                iframe_offset = await self.get_element_location_window_offset(iframe)
            else:
                iframe_offset = (await self.get_element_location_screen_offset(iframe))[
                    "html_web_element"
                ]
            ads_elements = None
            print(ads_elements_selector)
            ads_elements = await iframe.query_selector_all(ads_elements_selector)
            ads_elements_rect = []
            for ad_element in ads_elements:
                rect = ad_element.rect.copy()
                if self.device_type == "smartphone":
                    rect["x"] = iframe_offset["x_offset"] + rect["x"]
                    rect["y"] = iframe_offset["y_offset"] + rect["y"]
                else:
                    rect["x"] = iframe_offset[0] + rect["x"]
                    rect["y"] = iframe_offset[1] + rect["y"]
                rect["text_content"] = ad_element.text_all()
                ads_elements_rect.append(rect)
            self.web_browser_driver.switch_to.default_content()
            return ads_elements_rect

        if ads_elements_selector.startswith("//iframe"):
            ads_elements_selector = ads_elements_selector[10:]
            return await iframe_check()

    async def set_ad_behaviour_environment(
        self,
        ad_to_click,
        vignette_ad_close,
        vignette_ad_open,
        in_page_ad_links_open,
        ad_keywords=None,
    ):
        self.ad_to_click = ad_to_click

        self.vignette_ad_close = vignette_ad_close
        self.vignette_ad_open = vignette_ad_open

        self.in_page_ad_links_open = in_page_ad_links_open
        self.ad_keywords = ad_keywords

    async def close_ad(self):
        pass

    async def ad_click(self, ad_dimensions: dict, revert_back=False):
        if self.device_type == "computer":
            previous_mouse_pos = pyautogui.position()
            await self.simulate_human_mouse_move_behavior_to_area(
                ad_dimensions["x"],
                ad_dimensions["y"],
                ad_dimensions["width"],
                ad_dimensions["height"],
                probability_of_overshoot=round(random.random(), 2),
            )
            await asyncio.sleep(random.uniform(0.1, 0.4))
            pyautogui.click()
            if revert_back:
                await self.revert_to_main_page()
            await self.simulate_human_mouse_move_behavior_to_point(
                previous_mouse_pos[0], previous_mouse_pos[1]
            )
            return True
        elif self.device_type == "smartphone":
            self.touch.tap(
                ad_dimensions["x"] + random.uniform(0, ad_dimensions["width"]),
                ad_dimensions["y"] + random.uniform(0, ad_dimensions["height"]),
            )
            if revert_back:
                self.revert_to_main_page()
            return True
