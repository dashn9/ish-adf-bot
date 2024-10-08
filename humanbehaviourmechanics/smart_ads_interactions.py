import random
import time
import asyncio

import pyautogui

from log import logger


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
            logger.info("$$$ Attempting To Open Vignette Ad... $$$")
            await self.trigger_vignette(open_vignette=True)
            await asyncio.sleep(0.6)
            if tab_length != len(self.web_browser_driver.tabs):
                logger.info("$$$ Vignette Ad Opened $$$")
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
            # Switching this way is wrong, recently triggered tabs are always next to the active one not the last
            # I.E either switch to the next one [1] or find the currently active tab and switch to it's next
            self.active_tab = self.web_browser_driver.tabs[-1]
            await self.active_tab.activate()
        return ad_click_success
        # print(f"Bot Process Id {self.bot_process_id} <:::> No ads found, Try again")

    async def locate_ad_elements_in_iframe(self, ads_elements_selector):
        async def iframe_check():
            try:
                iframe = await self.active_tab.select("iframe", timeout=2)
            # Iframe not found
            except asyncio.TimeoutError:
                return
            if self.identity.device_type == "smartphone":
                document_offset = {"x": 0, "y": 0}
            else:
                document_offset = await self.get_document_offset_from_screen()
            ads_elements = await iframe.query_selector_all(ads_elements_selector)
            ads_elements_rect = []
            # You would need to make upgrades before ad keyword click would work with vignettes
            for ad_element in ads_elements:
                element_position = await ad_element.get_position()
                rect = {
                    # normally i'm supposed to add it with the browser's x position, but i'm going assume it's going to be 0
                    "x": element_position.x + document_offset.get("x"),
                    "y": element_position.y + document_offset.get("y"),
                    "width": element_position.width,
                    "height": element_position.height,
                    "text_content": ad_element.text_all,
                }
                ads_elements_rect.append(rect)
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
        if self.identity.device_type == "computer":
            previous_mouse_pos = pyautogui.position()
            await self.simulate_human_mouse_move_behavior_to_area(
                ad_dimensions["x"],
                ad_dimensions["y"],
                ad_dimensions["width"] + ad_dimensions["x"],
                ad_dimensions["height"] + ad_dimensions["y"],
                probability_of_overshoot=round(random.random(), 2),
            )
            await asyncio.sleep(random.uniform(0.1, 0.4))
            pyautogui.click()
            await asyncio.sleep(random.uniform(0.1, 0.4))
            if revert_back:
                await self.revert_to_active_page()
            await self.simulate_human_mouse_move_behavior_to_point(
                previous_mouse_pos[0], previous_mouse_pos[1]
            )
            return True
        elif self.identity.device_type == "smartphone":
            await self.touch.tap(
                ad_dimensions["x"] + random.uniform(0, ad_dimensions["width"]),
                ad_dimensions["y"] + random.uniform(0, ad_dimensions["height"]),
            )
            if revert_back:
                self.revert_to_active_page()
            return True
