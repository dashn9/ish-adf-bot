import asyncio
import json
import os
import random
import time
import tempfile
from functools import reduce

from nodriver import Element as WebElement, Tab, Browser
import nodriver as uc

from bots import utils
from bots.devtools import devtools_primary
from constants import bot_constants, browser_constants, config





# I created this to fix the issue with nodriver browser start not waiting long enough
from nodriver.core.browser import HTTPApi
import asyncio
import logging
import pathlib
import warnings
from nodriver import cdp
from nodriver.core.browser import util
from nodriver.core._contradict import ContraDict
from nodriver.core.config import is_posix
from nodriver.core.connection import Connection

logger = logging.getLogger(__name__)
class ExtendingBrowser(Browser):
    _http: HTTPApi = None
    async def start(self=None) -> Browser:
        """launches the actual browser"""
        if not self:
            warnings.warn("use ``await Browser.create()`` to create a new instance")
            return

        if self._process or self._process_pid:
            if self._process.returncode is not None:
                return await self.create(config=self.config)
            warnings.warn("ignored! this call has no effect when already running.")
            return

        # self.config.update(kwargs)
        connect_existing = False
        if self.config.host is not None and self.config.port is not None:
            connect_existing = True
        else:
            self.config.host = "127.0.0.1"
            self.config.port = util.free_port()

        if not connect_existing:
            logger.debug(
                "BROWSER EXECUTABLE PATH: %s", self.config.browser_executable_path
            )
            if not pathlib.Path(self.config.browser_executable_path).exists():
                raise FileNotFoundError(
                    (
                        """
                    ---------------------
                    Could not determine browser executable.
                    ---------------------
                    Make sure your browser is installed in the default location (path).
                    If you are sure about the browser executable, you can specify it using
                    the `browser_executable_path='{}` parameter."""
                    ).format(
                        "/path/to/browser/executable"
                        if is_posix
                        else "c:/path/to/your/browser.exe"
                    )
                )

        if getattr(self.config, "_extensions", None):  # noqa
            self.config.add_argument(
                "--load-extension=%s"
                % ",".join(str(_) for _ in self.config._extensions)
            )  # noqa

        exe = self.config.browser_executable_path
        params = self.config()

        logger.info(
            "starting\n\texecutable :%s\n\narguments:\n%s", exe, "\n\t".join(params)
        )
        if not connect_existing:
            self._process: asyncio.subprocess.Process = (
                await asyncio.create_subprocess_exec(
                    # self.config.browser_executable_path,
                    # *cmdparams,
                    exe,
                    *params,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    close_fds=is_posix,
                )
            )
            self._process_pid = self._process.pid

        self._http = HTTPApi((self.config.host, self.config.port))
        util.get_registered_instances().add(self)
        await asyncio.sleep(1)
        for _ in range(10):
            try:
                self.info = ContraDict(await self._http.get("version"), silent=True)
            except (Exception,):
                if _ == 4:
                    logger.debug("could not start", exc_info=True)
                await self.sleep(1)
            else:
                break

        if not self.info:
            raise Exception(
                (
                    """
                ---------------------
                Failed to connect to browser
                ---------------------
                One of the causes could be when you are running as root.
                In that case you need to pass no_sandbox=True 
                """
                )
            )

        self.connection = Connection(self.info.webSocketDebuggerUrl, _owner=self)

        if self.config.autodiscover_targets:
            logger.info("enabling autodiscover targets")

            # self.connection.add_handler(
            #     cdp.target.TargetInfoChanged, self._handle_target_update
            # )
            # self.connection.add_handler(
            #     cdp.target.TargetCreated, self._handle_target_update
            # )
            # self.connection.add_handler(
            #     cdp.target.TargetDestroyed, self._handle_target_update
            # )
            # self.connection.add_handler(
            #     cdp.target.TargetCreated, self._handle_target_update
            # )
            #
            self.connection.handlers[cdp.target.TargetInfoChanged] = [
                self._handle_target_update
            ]
            self.connection.handlers[cdp.target.TargetCreated] = [
                self._handle_target_update
            ]
            self.connection.handlers[cdp.target.TargetDestroyed] = [
                self._handle_target_update
            ]
            self.connection.handlers[cdp.target.TargetCrashed] = [
                self._handle_target_update
            ]
            await self.connection.send(cdp.target.set_discover_targets(discover=True))
        await self
        # self.connection.handlers[cdp.inspector.Detached] = [self.stop]
        # return self





class BrowserInterface:
    def __init__(self, browser_to_use_id=browser_constants.CHROME_ID,
                 bot_process_id=None, timezone_id=None, device_type="computer", hardware_concurrency=2,
                 has_touch="no_touch", has_mouse="no_mouse", languages=["en-US", "en"], user_agent=None, hardware=None,
                 platform={}, screen_width=1920, screen_height=1080, device_pixel_ratio=1, cookies=list(),
                 identity_id=None, cookies_update_callback=None):
        self.web_browser_driver: uc.Browser = None
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
        self.hardware_concurrency=hardware_concurrency
        self.platform = platform
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.device_pixel_ratio = device_pixel_ratio
        self.cookies = cookies
        self.cookies_update_callback = cookies_update_callback
        self.identity_id = identity_id
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

    async def get_scroll_bar_coordinates(self, relative_to=0):
        """
        Calculates And Returns The Prospective Location And Dimesion Of The Browser Scrollbar
        :param relative_to: To Determine The Boundaries By Which To Calculate The Positions
        :return: The Position And Dimensions Of The ScrollBar In A Dictionary, False If No Scroll Bar Exists
        """
        browser_window_body_size = await self.get_browser_window_body_size()

        browser_inner_size = await self.get_browser_inner_size()

        if browser_window_body_size.get("height") <= browser_inner_size.get("height"):
            # No Scrollbar
            return False

        # Fetch Browser Document Inner Offset
        window_page_y_offset = await self.active_tab.evaluate("window.pageYOffset")
        window_page_y_offset = 1 if window_page_y_offset <= 0 else window_page_y_offset

        browser_outer_size = dict(width=await self.active_tab.evaluate("window.outerWidth", await_promise=True),
                                  height=await self.active_tab.evaluate("window.outerHeight", await_promise=True))

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
            browser_rect = self.active_tab.get_window()
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
            browser_rect = await self.active_tab.get_window()
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
        return {"y_offset": await self.active_tab.evaluate("window.pageYOffset", await_promise=True),
                "x_offset": await self.active_tab.evaluate("window.pageXOffset", await_promise=True)}

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
                                         {"width": self.screen_width,
                                          "height": self.screen_height, "device_scale_factor":
                                              self.device_pixel_ratio, "screen_orientation":
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


                        # I do not like this solution one bit because if the program was meant to be running at loop, it terminates.
                        # I do not have a choice as I do not have a way to exit the current function. except i have a way to pass an event.
                        asyncio.get_event_loop().stop()
                        exit()
                except ConnectionRefusedError:
                    print(
                        "A connection refused error occurred, this would likely be as a result of a dead browser session")
            else:
                asyncio.create_task(self.quit_browser_after_max_alive(sleep_time=5))

    @staticmethod
    async def _handle_prefs(options):
        if prefs := options.experimental_options.get("prefs"):
            # turn a (dotted key, value) into a proper nested dict
            async def un_dot_key(key, value):
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

    async def open_web_browser(self):
        open_browser_in_full_screen = True
        window_size = (self.screen_width, self.screen_height)
        # An 8% chance and device is pc that randomly resize the web browser in a manner that is un-obstructive
        if random.random() >= browser_constants.MAXIMUM_WINDOW_PROBABILITY and self.device_type == "computer":
            open_browser_in_full_screen = False
            window_size = utils.fetch_random_window_size_relative_to_screen(*window_size)
        # Opens a Chrome browser
        if self.browser_to_use_id == browser_constants.CHROME_ID:
            print(f"Bot Process Id {self.bot_process_id} <:::> Opening Chrome Browser")
            browser_config = uc.Config(browser_args=[
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--enable-logging=0',
                '--disable-remote-fonts',
                '--disable-dev-shm-usage',
                '--window-position=0,0',
                '--start-maximized'
                # supposed to help with storage usage, but i'm not sure
                ], user_data_dir=browser_constants.CHROME_DATA_DIRECTORY+"/profiles/"+str(self.identity_id), 
                browser_executable_path=bot_constants.FULL_DIRECTORY_PATH+browser_constants.CHROME_BINARY_LOCATION,
                sandbox=False)
            browser_config.add_extension(f'{bot_constants.FULL_DIRECTORY_PATH+browser_constants.CHROME_EXTENSIONS_LOCATION+"/browser_spoofer.crx"}')
            browser_config.add_extension(f'{bot_constants.FULL_DIRECTORY_PATH+browser_constants.CHROME_EXTENSIONS_LOCATION+"/browser_network.crx"}')
            if self.user_agent:
                browser_config.add_argument(f"--user-agent={self.user_agent}")
            browser_config.binary_location = browser_constants.CHROME_BINARY_LOCATION
            self.web_browser_driver = await ExtendingBrowser.create(
                config=browser_config)
            self.active_tab = self.web_browser_driver.main_tab
            await asyncio.sleep(0.6)
            if open_browser_in_full_screen:
                if random.random() <= browser_constants.FULLSCREEN_PROBABILITY:
                    await self.active_tab.set_window_state(0, 0, *window_size, state="fullscreen")
                elif config.CONTAINERIZED:
                    await self.active_tab.set_window_state(0, 0, *window_size, state="fullscreen")
                    await self.active_tab.set_window_state(0, 0, *window_size, state="maximized")
                else:
                    await self.active_tab.set_window_state(0, 0, *window_size, state="maximized")
            else:
                await self.active_tab.set_window_state(0, 0, *window_size)
            if self.device_type == "smartphone" and config.CONTAINERIZED:
                await self.active_tab.set_window_state(0, 0, bot_constants.SCREEN_WIDTH - 1, bot_constants.SCREEN_HEIGHT - 1)

        print(f"Bot Process Id {self.bot_process_id} <:::> Web Browser Opened")

        await self.preliminary_tab_activation(self.active_tab)
        await asyncio.sleep(1)
        await devtools_primary.set_all_cookies(self.web_browser_driver, await self.identity.fetch_identity_cookies_info_for_extension())
        await asyncio.sleep(1)
        self.preliminary_activated_tabs.add(self.active_tab.target.target_id)
        await devtools_primary.listen_to_tab_creation(self.web_browser_driver.connection, self._handle_new_tab_creation)
        # give browser time to settle
        await self.active_tab.sleep(4)
        asyncio.create_task(self.quit_browser_after_max_alive())

    async def _handle_new_tab_creation(self, new_tab):
        """This function is reasonably effective, however when there is a lot of traffic going to the client(most likely a page making a lot of network requests, or devtools input bombarding the browser(which is normal)), 
        This function looses effectiveness albeit not completely.

        A possible solution would be to suspend all cdp operations for a while giving time for prelimary_tab_activation to complete

        Args:
            new_tab (_type_): _description_
        """
        async def handle_page_lifecycle_events(lifecycle_event, *args, **kwargs):
            nonlocal continue_reload, tab, first_url
            if (tab.target.url != first_url):
                continue_reload = False
        async def tab_reloader_if_redirect_link(tab, old_url):
            pass
        for tab in self.web_browser_driver.tabs:
            continue_reload = True
            # Please find another efficient way to make sure the url hasn't loaded before attempting a change, you can use target url change in combination
            reload_count = 0
            first_url = None
            target_id = tab.target.target_id
            if target_id not in self.preliminary_activated_tabs:
                await tab.sleep(1.5)
                first_url = tab.target.url
                await devtools_primary.enable_page(tab)
                await devtools_primary.listen_to_page_lifecycle(tab, handle_page_lifecycle_events)
                # The first url does not go through the proxy for obvious reasons as the tab was created with the url before adding the interceptor
                # I created an extension(browser_network) to help deal with this issue by stopping early requests
                await self.preliminary_tab_activation(tab)
                self.preliminary_activated_tabs.add(target_id)
                # requires fix
                while continue_reload and (reload_count < 4):
                    await tab.reload()
                    print("reload triggered", reload_count)
                    await tab.sleep(3)
                    reload_count += 1


    async def preliminary_tab_activation(self, target_tab: Tab):
        await self.add_network_interception_to_tab(target_tab)
        await asyncio.sleep(0.5)
        print(f"Bot Process Id {self.bot_process_id} <:::> Activating Browser Based On Device Type")
        # If device to emulate is a smartphone, set chrome to mobile mode
        if self.device_type == "smartphone":
            print(f"Bot Process Id {self.bot_process_id} <:::> Device Name:", self.hardware)
            await self.activate_mobile(target_tab)
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Page To Always Be In Focus")
        print(f"Bot Process Id {self.bot_process_id} <:::> Setting Timezone From Identity")
        await target_tab.sleep(0.5)
        await devtools_primary.set_hardware_concurrency(target_tab, self.hardware_concurrency)
        # Set Timezone
        await devtools_primary.set_timezone(target_tab, self.timezone_id)
        # If identity has a user agent, change browser user agent to identity's
        if self.user_agent:
            print(
                f"Bot Process Id {self.bot_process_id} <:::> Setting User Agent: {self.user_agent} From Identity")
            await devtools_primary.change_user_agent(
                target_tab,
                self.user_agent, self.platform, self.languages, self.identity.browser_name, self.identity.device_type == "smartphone", self.identity.device_model)

    async def add_network_interception_to_tab(self, target_tab: Tab):
        await devtools_primary.enable_network_interception(target_tab)
        await devtools_primary.add_request_interception(target_tab, await self.request_interceptor(target_tab))
