# With Great Power Comes Great Responsibility

from browsers.browser_interface import BrowserInterface
from constants import browser_constants, bot_constants
from humanbehaviourmechanics.smart_human_reader import SmartHumanReader
from identity.client import Identity
from network.network_processors import NetworkRunner


class WebBot(
    BrowserInterface, SmartHumanReader, NetworkRunner
):  # A powerful WebBot designed to visit and perform activities on given url/s

    def __init__(
        self,
        identity=None,
        browser_to_use_id=browser_constants.CHROME_ID,
        bot_process_id=None,
        no_of_clicks=0,
    ):
        self.bot_process_id = bot_process_id
        if browser_to_use_id == browser_constants.CHROME_ID:
            browser_name = "chrome"
        elif browser_to_use_id == browser_constants.FIREFOX_ID:
            browser_name = "firefox"
        else:
            browser_name = "chrome"
        if not identity:
            self.identity = Identity(
                id=0,
                device_type="is_pc",
                hardware="Desktop",
                platform={
                    "architecture": None,
                    "bitness": None,
                    "navigator_platform": None,
                    "name": "Win32",
                    "version": None,
                },
                canvas_fp_offset=[0, 0, 0, -1],
                audio_context_fp_offset=0.2,
                font_fp_offset=[1, 1],
                webgl_fp_offset=[0.9343, 0.3453],
                hardware_concurrency=4,
                memory=4,
                has_mouse="has_mouse",
                has_battery="no_battery",
                has_touch="no_touch",
                browser_name=browser_name,
                browser_version=None,
                screen_resolution=None,
                gpu_vendor="Google Inc. (Intel)",
                gpu_renderer="Intel(R) HD Graphics",
                referer="https://l.facebook.com",
                reading_speed=900,
                timezone=["Etc/GMT", 0, "AM Coordinated Time"],
                mouse_delta_y=50,
            )
        else:
            self.identity = identity

        NetworkRunner.__init__(self, bot_process_id, identity, bot_constants.USE_PROXY)

        BrowserInterface.__init__(
            self,
            browser_to_use_id=browser_to_use_id,
            bot_process_id=bot_process_id,
            timezone_id=identity.timezone[0],
            device_type=identity.device_type,
            has_touch=identity.has_touch,
            has_mouse=identity.has_mouse,
            languages=identity.languages,
            user_agent=identity.user_agent,
            hardware=identity.hardware,
            platform=identity.platform,
            screen_width=identity.screen_width,
            screen_height=identity.screen_height,
            device_pixel_ratio=identity.screen_resolution["density_pixel_ratio"],
            cookies=identity.cookies,
            identity_id=identity.id,
            cookies_update_callback=identity.update_cookies,
        )

        SmartHumanReader.__init__(
            self,
            reading_speed=identity.reading_speed,
            no_of_clicks=no_of_clicks,
        )
