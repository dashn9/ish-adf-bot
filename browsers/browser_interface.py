import asyncio
import json
import os
import random
import time
import tempfile
from functools import reduce

from nodriver import Element as WebElement, Tab
import nodriver as uc

from bots import utils
from bots.devtools import devtools_primary
from constants import bot_constants, browser_constants, config
from log import logger


class BrowserInterface:
    def __init__(self, identity, browser_to_use_id=browser_constants.CHROME_ID,
                 cookies_update_callback=None):
        self.web_browser_driver: uc.Browser = None
        self.time_activated = time.time()
        self.browser_to_use_id = browser_to_use_id
        self.opened_browser_urls = dict()
        self.identity=identity
        self.current_tab_length = 1
        self.cookies_update_callback = cookies_update_callback
        self.dom_storage = None
        self.preliminary_activated_tabs = set()
        self.active_tab = None

    async def update_cookies_to_cloud(self):
        if self.cookies_update_callback:
            return await self.cookies_update_callback(await self.fetch_all_cookies())
            # self.identity.update_cookies() put in the callback
        else:
            return self.fetch_all_cookies()

    async def open_new_tab(self, url):
        """
        param url: Url Location Of The WebPage
        return: Return True On Success
        """
        try:
            await self.active_tab.evaluate(f"window.open();", await_promise=True)
            self.web_browser_driver.switch_to.window(self.web_browser_driver.tabs[-1])
            if url:
                self.web_browser_driver.get(url)
            return self.web_browser_driver.current_window_handle
        except (NameError, TypeError):
            return False

    async def open_url_on_browser(self, url: str, url_name: str, force_browser_diversion=False):
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
                    self.opened_browser_urls[url_name] = self.web_browser_driver.tabs[0]
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

    async def get_browser_window_body_size(self):
        return dict(width=await self.active_tab.evaluate("document.body.getBoundingClientRect().width", await_promise=True),
                    height=await self.active_tab.evaluate(
                        "document.body.getBoundingClientRect().height", await_promise=True))

    async def get_browser_inner_size(self):
        return dict(width=await self.active_tab.evaluate("window.innerWidth", await_promise=True),
                    height=await self.active_tab.evaluate("window.innerHeight", await_promise=True))

    async def get_element_location_screen_offset(self, html_web_element: WebElement):
        """
        Calculate And Return Both Window And Element Location Offsets Relative To Screen
        :param html_web_element: Target HTML Element
        :return: Offset Locations Of Element(tuple) And Browser(tuple) In a Dict()
        """
        # Getting HTML Web Element Coordinates Which Are Relative From The Window Point And Dimensions
        try:
            web_element_location_dimensions = await html_web_element.get_position()
        except:
            web_element_location_dimensions = await html_web_element.get_position()

        document_offset_from_screen = await self.get_document_offset_from_screen()

        browser_window_rect = (await self.active_tab.get_window())[1]

        web_element_x_offset = web_element_location_dimensions.x + document_offset_from_screen['x']
        web_element_y_offset = web_element_location_dimensions.y + document_offset_from_screen['y']

        browser_window_rect_bottom = browser_window_rect.height + browser_window_rect.top
        web_element_bottom = web_element_y_offset + web_element_location_dimensions.height
        return {"html_web_element": {"x_offset": web_element_x_offset, "y_offset": web_element_y_offset,
                                    "width": web_element_location_dimensions.width, "height": web_element_location_dimensions.height, "bottom": web_element_bottom},
                "browser_window_rect": (
                    browser_window_rect.left, browser_window_rect.top, browser_window_rect_bottom)}

    async def get_document_offset_from_screen(self):
        """
        This method calculates the dimensions of the document page of a browser relative to the screen. It might not be accurate, if there is an addition component in the tab e.g devtools
        :return: A dictionary holding document dimensions
        """
        browser_inner_size = await self.get_browser_inner_size()
        browser_window_rect = (await self.active_tab.get_window())[1]
        # In the case of mobile devices, the browser inner size could potentially be larger than it's window size
        # It helps with y but not with x
        return dict(y=browser_window_rect.top + max((browser_window_rect.height - browser_inner_size["height"]), 0),
                    x=browser_window_rect.left + max((browser_window_rect.width - browser_inner_size["width"]), 0),
                    width=browser_inner_size["width"], height=browser_inner_size["height"])

    async def get_element_location_window_offset(self, html_web_element: WebElement):
        """
        Calculate And Return Both Element Location Offsets Relative To Window
        :param html_web_element: Target HTML Element
        :return: Offset Locations Of Element(tuple) And Browser(tuple) In a Dict()
        """
        # Getting HTML Web Element Coordinates Which Are Relative From The Window Point) And Dimensions
        try:
            web_element_location_dimensions = await html_web_element.get_position()
        except:
            # I know this is not right, will look for a better fix in the future, this one is urgent
            web_element_location_dimensions = await html_web_element.get_position()


        web_element_x_offset = web_element_location_dimensions.x
        web_element_y_offset = web_element_location_dimensions.y

        web_element_bottom = web_element_y_offset + web_element_location_dimensions.height
        return {"x_offset": web_element_x_offset, "y_offset": web_element_y_offset, "bottom": web_element_bottom}

    async def get_window_document_offsets(self):
        # return values of evaluate ends up as None if it's actually 0, issue is from nodriver
        return {"y_offset": (await self.active_tab.evaluate("window.pageYOffset", await_promise=True)) or 0,
                "x_offset": (await self.active_tab.evaluate("window.pageXOffset", await_promise=True)) or 0}
    
    async def get_window_document_bounds(self):
        logger.info("{{{ Fetching Document Offsets... }}}")
        offsets = await self.get_window_document_offsets()
        logger.info("{{{ Fetching Document Bounds... }}}")
        bounds = await self.get_browser_inner_size()
        return dict(**offsets, **bounds, bottom=bounds.get("height") + offsets.get("y_offset"))
    
    async def bring_window_to_front(self):
        await self.active_tab.bring_to_front()

    async def revert_to_active_page(self, recurse=False, time_interval_to_check=0.4):
        """
        Returns page to main if changed
        :param time_interval_to_check: number of seconds to wait for before checking, set to zero if wanted instantly
        :return: True if page changed, else false
        """
        await asyncio.sleep (time_interval_to_check)
        if self.current_tab_length != len(self.web_browser_driver.tabs):
            await self.active_tab.activate()
            self.current_tab_length = len(self.web_browser_driver.tabs)
            if recurse:
                await self.revert_to_active_page(recurse, time_interval_to_check)
            return True
        if recurse:
            await self.revert_to_active_page(recurse, time_interval_to_check)
        return False

    async def activate_mobile(self, target_tab: Tab):
        await devtools_primary.activate_mobile(target_tab,
                                         {"width": self.identity.screen_resolution.get("logical_width"),
                                          "height": self.identity.screen_resolution.get("logical_height"), "device_scale_factor":
                                              self.identity.screen_resolution.get("density_pixel_ratio", 1), "screen_orientation":
                                              {"type": "portrait_primary", "angle": 0},
                                          "mobile": True})

    async def fetch_all_cookies(self):
        cookies = await devtools_primary.get_all_cookies(self.web_browser_driver)
        return [cookie.to_json() for cookie in cookies]

    async def quit_browser_after_max_alive(self, sleep_time=bot_constants.BOT_MIN_ALIVE_TIME):
        await asyncio.sleep (sleep_time)
        if hasattr(self, "web_browser_driver"):
            if time.time() - self.time_activated > bot_constants.BOT_MAX_ALIVE_TIME + random.uniform(-6.5, 6.5):
                print(f"Identity: {self.identity_id} On Process: {self.bot_process_id} Could Not Perform "
                      f"Activity Within Set Time, Exiting Session...")
                try:
                    if not self.web_browser_driver.stopped:
                        print(f"Bot Process Id {self.bot_process_id} <:::> Updating Cookies To Cloud")
                        await self.update_cookies_to_cloud()
                        self.web_browser_driver.stop()
                        await asyncio.sleep(0.5)


                    # I do not like this solution one bit because if the program was meant to be running at loop, it terminates.
                    # I do not have a choice as I do not have a way to exit the current function. except i have a way to pass an event.
                    asyncio.get_event_loop().stop()
                    exit()
                except ConnectionRefusedError:
                    print(
                        "A connection refused error occurred, this would likely be as a result of a dead browser session")
            else:
                asyncio.create_task(self.quit_browser_after_max_alive(sleep_time=5))

    async def open_web_browser(self):
        open_browser_in_full_screen = True
        window_size = (self.identity.screen_width, self.identity.screen_height)
        if random.random() >= browser_constants.MAXIMUM_WINDOW_PROBABILITY and self.identity.device_type == "computer":
            open_browser_in_full_screen = False
            window_size = utils.fetch_random_window_size_relative_to_screen(*window_size)
        user_data_dir = browser_constants.CHROME_DATA_DIRECTORY+"/profiles/"+str(self.identity.id)
        utils.remove_profile_lock(user_data_dir)
        # Opens a Chrome browser
        if self.browser_to_use_id == browser_constants.CHROME_ID:
            browser_config = uc.Config(browser_args=[
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--enable-logging=0',
                '--disable-remote-fonts',
                '--disable-dev-shm-usage',
                '--window-position=0,0',
                '--start-maximized'
                ], user_data_dir=user_data_dir, 
                browser_executable_path=bot_constants.FULL_DIRECTORY_PATH+browser_constants.CHROME_BINARY_LOCATION)
            browser_config.add_extension(f'{bot_constants.FULL_DIRECTORY_PATH+browser_constants.CHROME_EXTENSIONS_LOCATION+"/browser_spoofer.crx"}')
            browser_config.add_extension(f'{bot_constants.FULL_DIRECTORY_PATH+browser_constants.CHROME_EXTENSIONS_LOCATION+"/browser_network.crx"}')
            browser_config.add_argument(f"--user-agent={self.identity.user_agent}")
            browser_config.binary_location = browser_constants.CHROME_BINARY_LOCATION
            logger.info("{{{ Opening Chrome Browser... }}}")
            self.web_browser_driver = await uc.start(
                config=browser_config,
                sandbox=False)
            logger.info("{{{ Web Browser Opened }}}")
            self.active_tab = self.web_browser_driver.main_tab
            if open_browser_in_full_screen:
                # Full screen behaves like kiosk mode on containers, plus it's buggy and much to deal with so.
                if random.random() <= browser_constants.FULLSCREEN_PROBABILITY and not config.CONTAINERIZED:
                    logger.info("{{{ Setting Window Size To Fullscreen... }}}")
                    await self.active_tab.set_window_state(0, 0, *window_size, state="fullscreen")
                elif config.CONTAINERIZED:
                    logger.info("{{{ Setting Window Size To Maximized: Container Method... }}}")
                    await self.active_tab.set_window_state(0, 0, *window_size, state="fullscreen")
                    await self.active_tab.set_window_state(0, 0, *window_size, state="maximized")
                else:
                    logger.info("{{{ Setting Window Size To Maximized... }}}")
                    await self.active_tab.set_window_state(0, 0, *window_size, state="maximized")
            else:
                logger.info("{{{ Setting Window Size To: %d,%d... }}}" % window_size)
                await self.active_tab.set_window_state(0, 0, *window_size)
            if self.identity.device_type == "smartphone" and config.CONTAINERIZED:
                await self.active_tab.set_window_state(0, 0, bot_constants.SCREEN_WIDTH - 1, bot_constants.SCREEN_HEIGHT - 1)
        await asyncio.sleep(0.8)
        logger.info("{{{ Activating Tab Preliminarily... }}}")
        await self.preliminary_tab_activation(self.active_tab)
        await asyncio.sleep(0.8)
        self.preliminary_activated_tabs.add(self.active_tab.target.target_id)
        logger.info("{{{ Adding Listener to New Tabs Creation... }}}")
        await devtools_primary.listen_to_tab_creation(self.web_browser_driver.connection, self._handle_new_tab_creation)
        logger.info("{{{ Opening Blank Website... }}}")
        await self.active_tab.get('https://blank.org')
        await asyncio.sleep(1)
        logger.info("{{{ Executing JS: Dispatching Event With Identity Spoof Data... }}}")
        # The purpose of these code below is to be able to dispatch an event to the extension, which only comes alive after a url load
        identitySpoofData = json.dumps(await self.identity.fetch_identity_data_for_extension())
        await self.active_tab.evaluate(f"""
            window.dispatchEvent(new CustomEvent('ishBotSpoofData', {{ detail: {identitySpoofData} }}));
        """)
        # consider moving this to a thread instead
        asyncio.create_task(self.quit_browser_after_max_alive())

    async def _handle_new_tab_creation(self, new_tab):
        """This function is reasonably effective, however when there is a lot of traffic going to the client(most likely a page making a lot of network requests, or devtools input bombarding the browser(which is normal)), 
        This function looses effectiveness albeit not completely.

        A possible solution would be to suspend all cdp operations for a while giving time for prelimary_tab_activation to complete

        Args:
            new_tab (_type_): _description_
        """
        for tab in self.web_browser_driver.tabs:
            target_id = tab.target.target_id
            if target_id not in self.preliminary_activated_tabs:
                logger.info("{{{ New Tab Discovered: %s }}}" % (target_id))
                logger.info("{{{ Enabling Page Events For Tab: %s }}}" % (target_id))
                await devtools_primary.enable_page(tab)
                logger.info("{{{ Activating Tab: %s Preliminarily... }}}" % (target_id))
                await self.preliminary_tab_activation(tab)
                await time.sleep(2)
                logger.info("{{{ Reloading Tab: %s... }}}" % (target_id))
                await tab.reload()


    async def preliminary_tab_activation(self, target_tab: Tab):
        target_id = target_tab.target.target_id
        logger.info("{{{ Adding Network Interception to Tab: %s... }}}" % (target_id))
        await self.add_network_interception_to_tab(target_tab)
        await asyncio.sleep(0.5)
        # If device to emulate is a smartphone, set chrome to mobile mode
        if self.identity.device_type == "smartphone":
            logger.info("{{{ Activating Mobile On Browser For Device: %s... }}}" % (self.identity.hardware))
            await self.activate_mobile(target_tab)
        await target_tab.sleep(0.5)
        logger.info("{{{ Setting Hardware Concurrency: %d... }}}" % (self.identity.hardware_concurrency))
        await devtools_primary.set_hardware_concurrency(target_tab, self.identity.hardware_concurrency)
        logger.info("{{{ Setting Up Timezone: %s... }}}" % (self.identity.timezone.get("id")))
        await devtools_primary.set_timezone(target_tab, self.identity.timezone.get("id"))
        logger.info("{{{ Activating FULL_USER_AGENT For Identity... }}}")
        await devtools_primary.change_user_agent(
            target_tab,
            self.identity.user_agent, self.identity.platform, self.identity.languages, self.identity.browser_name, self.identity.device_type == "smartphone", self.identity.device_model)

    async def add_network_interception_to_tab(self, target_tab: Tab):
        await devtools_primary.enable_network_interception(target_tab)
        await devtools_primary.add_request_interception(target_tab, await self.request_interceptor(target_tab))
