import json
import random
import string
import subprocess
import time

from datacontroller.datacontroller import DataController
from constants import bot_constants
from bots import utils


class Identity:
    ovpn_process = None

    def __init__(
        self,
        id=None,
        device_type="",
        hardware="",
        os="",
        os_version="",
        platform={
            "architecture": None,
            "bitness": None,
            "navigator_platform": None,
            "name": None,
            "version": None,
        },
        canvas_fp_offset=None,
        audio_context_fp_offset=None,
        font_fp_offset=None,
        webgl_fp_offset=None,
        hardware_concurrency=None,
        memory=None,
        device_model=None,
        has_mouse=None,
        has_battery=None,
        has_touch=None,
        browser_name="",
        browser_version="",
        screen_resolution=None,
        gpu_vendor="",
        gpu_renderer="",
        proxy_client="",
        proxy_geo="",
        referer="",
        reading_speed=None,
        timezone=None,
        languages=["en-US", "en"],
        mouse_delta_y=None,
        ad_click_probability=0.1,
        ad_provider="",
        ad_type_to_click="in_page",
        ad_keywords=[],
        ad_keywords_click_probability=0.2,
        cookies=list(),
    ):
        self._raw_identity = None
        self.id = id
        self.device_type = device_type
        self.hardware = hardware
        self.os = os
        self.os_version = os_version
        self.platform = platform
        self.canvas_fp_offset = canvas_fp_offset
        self.audio_context_fp_offset = audio_context_fp_offset
        self.font_fp_offset = font_fp_offset
        self.webgl_fp_offset = webgl_fp_offset
        self.hardware_concurrency = hardware_concurrency
        self.memory = memory
        self.device_model = device_model
        self.has_mouse = has_mouse
        self.has_battery = has_battery
        self.has_touch = has_touch
        self.browser_name = browser_name
        self.browser_version = browser_version
        self.screen_resolution = screen_resolution
        if isinstance(screen_resolution, dict):
            self.screen_width = screen_resolution["logical_width"]
            self.screen_height = screen_resolution["logical_height"]
        else:
            self.screen_width = 1920
            self.screen_height = 1080
        self.gpu_vendor = gpu_vendor
        self.gpu_renderer = gpu_renderer
        self.proxy_client = proxy_client
        self.proxy_geo = proxy_geo
        self.referer = referer
        self.referrals = None
        self.reading_speed = reading_speed
        self.user_agent = None
        self.timezone = timezone
        self.languages = languages
        self.mouse_delta_y = mouse_delta_y
        self.cookies = cookies
        self.improvised_public_ip = False
        self.invalid_proxy = False
        self.page_depth = 0.3
        self.ad_provider = ad_provider
        self.ad_click_probability = ad_click_probability
        self.ad_type_to_click = ad_type_to_click
        self.ad_keywords = ad_keywords
        self.ad_keywords_click_probability = ad_keywords_click_probability

        self.data_controller = DataController()

        self.is_vpn_connected = True
        self.proxy_url = None
        self.proxy_release_url = None

    def resolve_identity_from_cloud(self, method, value):
        identity = self.data_controller.fetch_an_identity(method, value)
        if not identity:
            raise ValueError(
                "Identity Fetched Does Not Appear To Be What It Is, Something Has To Be Wrong With Given"
                "Parameters"
            )
        print("Successfully Fetched An Identity With ID:", identity["ID"])
        print("Resolving Details To Identity Object")
        self.id = identity["ID"]
        self.device_type = identity["DEVICE_TYPE"]
        self.hardware = identity["HARDWARE"]
        self.os = identity["OS"]
        self.os_version = identity["OS_VERSION"]
        self.platform = identity["PLATFORM"]
        self.canvas_fp_offset = identity["FINGERPRINT"]["canvas_offset"]
        self.audio_context_fp_offset = identity["FINGERPRINT"]["audio_context_offset"]
        self.font_fp_offset = identity["FINGERPRINT"]["font_offset"]
        self.webgl_fp_offset = identity["FINGERPRINT"]["webgl_offset"]
        self.hardware_concurrency = identity["HARDWARE_CONCURRENCY"]
        self.memory = identity["MEMORY"]
        self.device_model = identity["DEVICE_MODEL"]
        self.has_mouse = identity["HAS_MOUSE"]
        self.has_battery = identity["HAS_BATTERY"]
        self.has_touch = identity["HAS_TOUCH"]
        self.browser_name = identity["BROWSER"]
        self.browser_version = identity["BROWSER_VERSION"]
        identity["SCREEN_RESOLUTION"] = identity["SCREEN_RESOLUTION"]
        self.screen_resolution = identity["SCREEN_RESOLUTION"]
        if isinstance(self.screen_resolution, dict):
            self.screen_width = self.screen_resolution["logical_width"]
            self.screen_height = self.screen_resolution["logical_height"]
        else:
            self.screen_width = 1920
            self.screen_height = 1080
        self.gpu_vendor = identity["GPU"]["vendor"]
        self.gpu_renderer = identity["GPU"]["webgl_renderer"]
        self.proxy_client = identity["PROXY_CLIENT"]
        self.proxy_geo = identity["PROXY_GEO"]
        identity["REFERRALS"] = identity["REFERRALS"]
        self.referrals = identity["REFERRALS"]
        self.referer = None
        self.reading_speed = identity["READING_SPEED"]
        self.user_agent = identity["USER_AGENT"]
        self.languages = identity["LANGUAGE"]
        self.mouse_delta_y = identity["MOUSE_DELTA_Y"]
        self.cookies = identity["COOKIES"]
        self.page_depth = identity["PAGE_DEPTH"]
        self.ad_click_probability = identity["ADS"]["click_probability"]
        self.ad_keywords = identity["ADS"]["keywords"]
        self.ad_keywords_click_probability = identity["ADS"][
            "keywords_click_probability"
        ]
        self.ad_type_to_click = identity["ADS"]["type"]
        self.proxy_url = identity.get("PROXY_URL")
        self.proxy_release_url = identity.get("PROXY_RELEASE_URL", None)
        self._raw_identity = identity

    def auto_initiate_identity(self, method, method_value):
        self.resolve_identity_from_cloud(method, method_value)
        self.user_agent = self.user_agent or self.form_user_agent(
            self.os,
            self.os_version,
            self.device_model,
            self.browser_name,
            self.browser_version,
        )
        self.resolve_timezone()
        # self.connect_vpn(self.vpn_client, self.ovpn_file_name)
        self.resolve_referer()

    def resolve_timezone(self):
        resolved_proxy_url = self.proxy_url if bot_constants.USE_PROXY else None
        if self.improvised_public_ip:
            geolocation = self.data_controller.fetch_geolocation_data(
                resolved_proxy_url
            )

            self.timezone = [
                geolocation["timezone"],
                geolocation["offset"] / 60,
                geolocation["continent"] + " " + geolocation["city"] + " Standard Time",
            ]
        elif self._raw_identity["TIMEZONE"]:
            self.timezone = [
                self._raw_identity["TIMEZONE"]["id"],
                self._raw_identity["TIMEZONE"]["offset"],
                self._raw_identity["TIMEZONE"]["full_name"],
            ]
        else:
            print("Resolving Timezone From Cloud")
            identity_timezone = self.data_controller.fetch_timezone(
                self.id, resolved_proxy_url
            )
            if identity_timezone and identity_timezone.get("id", None):
                self.timezone = [
                    identity_timezone["id"],
                    identity_timezone["offset"],
                    identity_timezone["full_name"],
                ]
            else:
                print("An empty timezone was resolved from cloud - fixing")
                geolocation = self.data_controller.fetch_geolocation_data(
                    resolved_proxy_url
                )
                if not geolocation:
                    # This will occur if proxy could not be successfully connected with
                    self.invalid_proxy = True
                    print("invalid proxy")
                    return
                else:
                    self.timezone = [
                        geolocation["timezone"],
                        geolocation["offset"] / 60,
                        geolocation["continent"]
                        + " "
                        + geolocation["city"]
                        + " Standard Time",
                    ]

            print("geo location: ", identity_timezone)
            print("Successfully Resolved Timezone")

    def resolve_referer(self):
        self.referer = random.choice(self.referrals)

    def update_cookies(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        self.data_controller.update_cookies(self.id, cookies)

    def fetch_referrer(self):
        return self.identity.referrals[
            random.randint(0, len(self.identity.referrals) - 1)
        ]

    def form_user_agent(
        self,
        os: str,
        os_version: str,
        device_model: str | None,
        browser_name: str,
        browser_version: list,
    ):
        def standard_browser_version_replacer(ua: str, browser_version: list):
            return (
                ua.replace("<apple_web_kit_version>", browser_version[0])
                .replace("<browser_version>", browser_version[1])
                .replace("<safari_version>", browser_version[2])
            )

        def edge_browser_version_replacer(ua: str, browser_version: list):
            return (
                ua.replace("<apple_web_kit_version>", browser_version[0])
                .replace("<chrome_version>", browser_version[1])
                .replace("<safari_version>", browser_version[2])
                .replace("<browser_version>", browser_version[3])
            )

        BROWSER_TEMPLATES = {
            "CHROME_ANDROID": "Mozilla/5.0 (Linux; <os> <os_version>; <model>) AppleWebKit/<apple_web_kit_version> (KHTML, like Gecko) Chrome/<browser_version> Mobile Safari/<safari_version>",
            "CHROME_IPHONE": "Mozilla/5.0 (<os>; CPU iPhone OS <os_version> like Mac OS X) AppleWebKit/<apple_web_kit_version> (KHTML, like Gecko) CriOS/<browser_version> Mobile/<model> Safari/<safari_version>",
            "CHROME_MACINTOSH": "Mozilla/5.0 (<os>; Intel Mac OS X <os_version>) AppleWebKit/<apple_web_kit_version> (KHTML, like Gecko) Chrome/<browser_version> Safari/<safari_version>",
            # The archtecture on the windows ua below should also be subjected to change, however no provision was made for it because all windows device is x64 as per the generator.
            # This was done considering the fact that most windows pc follow the (Windows NT 10.0; Win64; x64) pattern
            "CHROME_WINDOWS": "Mozilla/5.0 (<os> NT <os_version>; Win64; x64) AppleWebKit/<apple_web_kit_version> (KHTML, like Gecko) Chrome/<browser_version> Safari/<safari_Version>",
            "EDGE_WINDOWS": "Mozilla/5.0 (<os> NT <os_version>; Win64; x64) AppleWebKit/<apple_web_kit_version> (KHTML, like Gecko) Chrome/<chrome_version> Safari/<safari_version> Edg/<browser_version>",
            "SAFARI_MACINTOSH": "Mozilla/5.0 (<os>; Intel Mac OS X <os_version>) AppleWebKit/<apple_web_kit_version> (KHTML, like Gecko) Version/<browser_version> Safari/<safari_version>",
            "SAFARI_IPHONE": "Mozilla/5.0 (<os>; CPU iPhone OS <os_version> like Mac OS X) AppleWebKit/<apple_web_kit_version> (KHTML, like Gecko) Version/<browser_version> Mobile/15E148 Safari/<safari_version>",
        }
        user_agent = (
            BROWSER_TEMPLATES[browser_name.upper() + "_" + os.upper()]
            .replace("<os>", os)
            .replace("<os_version>", os_version.replace(".", "_"))
            .replace("<model>", device_model or "")
        )
        if browser_name == "edge":
            return edge_browser_version_replacer(user_agent, browser_version)
        else:
            return standard_browser_version_replacer(user_agent, browser_version)

    def disconnect_all_vpn(self):
        if Identity.ovpn_process is not None:
            print("Closing Program Openvpn Connection")
            Identity.ovpn_process.kill()
            self.is_vpn_connected = False
        else:
            print("Closing All Existing Openvpn Connections")
            ovpn_kill_command = "sudo killall openvpn"
            try:
                ovpn_kill_process = subprocess.Popen(
                    ovpn_kill_command.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                ovpn_kill_process.wait(10)
                self.is_vpn_connected = False
            except:
                pass

    def generate_unique_lowercase_numbers_characters(self, length=12):
        chars = string.ascii_lowercase + string.digits
        random.seed()
        return "".join(random.choice(chars) for _ in range(length))

    def resolve_proxy_url(self, geo_target, proxy_name="proxyrack.com"):
        """This Function is Deprecated, The Proxy URL is now resolved from backend."""
        if proxy_name in ["smartproxy.com", "proxyrack.com"]:
            if geo_target:
                proxy_url = bot_constants.PROXY_STICKY_TEMPLATE.replace(
                    "<geo_target_area>", bot_constants.PROXY_GEO_TARGET_AREA
                )
                proxy_url = proxy_url.replace("<port>", str(bot_constants.PROXY_PORT))
                proxy_url = proxy_url.replace("<user>", bot_constants.PROXY_USERNAME)
                proxy_url = proxy_url.replace("<geo_target>", geo_target)
                proxy_url = proxy_url.replace(
                    "<ss_duration>", str(bot_constants.PROXY_SESSION_DURATION)
                )
                proxy_url = proxy_url.replace(
                    "<ss_string>", self.generate_unique_lowercase_numbers_characters()
                )
                proxy_url = proxy_url.replace("<pass>", bot_constants.PROXY_PASSWORD)
                return proxy_url
            else:
                return bot_constants.PROXY_RANDOM_TEMPLATE
        return False

    def connect_vpn(self, vpn_client, vpn_file_name, **kwargs):
        if (
            "id" in kwargs.keys()
            and "username" in kwargs.keys()
            and "password" in kwargs.keys()
        ):
            vpn_account = {
                "ID": kwargs["id"],
                "USERNAME": kwargs["username"],
                "PASSWORD": kwargs["password"],
            }
        else:
            vpn_account = self.data_controller.fetch_vpn_account_details(vpn_client)

        if self.is_vpn_connected:
            self.disconnect_all_vpn()

        if vpn_client == "nordvpn":
            config_dir = bot_constants.NORDVPN_OVPN_FILE_PATH
        elif vpn_client == "ipvanish":
            config_dir = bot_constants.IPVANISH_OVPN_FILE_PATH
        else:
            raise ValueError("vpn client has to match either nordvpn or openvpn")

        bash_command = (
            f"sudo openvpn --config {config_dir + vpn_file_name}"
            f" --auth-user-pass {bot_constants.FULL_DIRECTORY_PATH}/identity/account_details.temp.conf "
            f"--auth-nocache --server-poll-timeout {bot_constants.OVPN_MAX_WAIT_TIME_TILL_IP_IMPROVISE}"
        )

        temp_acc_file = open(
            f"{bot_constants.FULL_DIRECTORY_PATH}/identity/account_details.temp.conf",
            "w",
        )
        temp_acc_file.write(vpn_account["USERNAME"] + "\n" + vpn_account["PASSWORD"])
        temp_acc_file.close()
        print(f"Connecting To OpenVPN({vpn_client}) Server On File: {vpn_file_name}")
        Identity.ovpn_process = subprocess.Popen(
            "exec " + bash_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        line_count = 0
        for line in Identity.ovpn_process.stdout:
            line = line.decode()
            line_count += 1
            if "AUTH_FAILED" in line:
                print(
                    "Account Details Seems To Be Ineffective --> id, username, password",
                    vpn_account["ID"],
                    vpn_account["USERNAME"],
                    vpn_account["PASSWORD"],
                )
                retries_left = bot_constants.MAX_OVPN_CONNECT_RETRIES
                if "retries_left" in kwargs.keys():
                    retries_left = kwargs["retries_left"]
                if retries_left > 0:
                    print("Retrying Account, Retries Left --> ", retries_left)
                    retries_left -= 1
                    self.connect_vpn(
                        vpn_client,
                        vpn_file_name,
                        id=vpn_account["ID"],
                        username=vpn_account["USERNAME"],
                        password=vpn_account["PASSWORD"],
                        retries_left=retries_left,
                    )
                else:
                    self.data_controller.update_vpn_account_status(
                        vpn_client, vpn_account["ID"], 0
                    )
                    print("Fetching New Account And Reconnecting")
                    self.connect_vpn(vpn_client, vpn_file_name)
                    break
            elif "Initialization Sequence Completed" in line:
                print(
                    "Account Details Valid, Connected Successfully : id, username, password -->",
                    vpn_account["ID"],
                    vpn_account["USERNAME"],
                    vpn_account["PASSWORD"],
                )
                self.data_controller.update_vpn_account_status(
                    vpn_client, vpn_account["ID"], 1
                )
                self.is_vpn_connected = True
                break
            elif (
                "Connection timed out" in line
                or "connection failed" in line
                or "connection-reset" in line
            ):
                print(
                    "OVPN Seems To Be Stuck Connecting, Most Probably A Dead OVPN Config File, Less Likely Internet "
                    "Issues(Check To Make Sure). Improvising New Ip Address Via Another OVPN Config File"
                )
                self.improvised_public_ip = True
                config_file = utils.fetch_random_file_name_from_directory(
                    config_dir, "ovpn"
                )
                self.connect_vpn(
                    vpn_client,
                    config_file,
                    id=vpn_account["ID"],
                    username=vpn_account["USERNAME"],
                    password=vpn_account["PASSWORD"],
                )
                break

            elif "Enter Auth" in line:
                print("No Potential Username And/Or Password Found In Configuration")
                self.data_controller.update_vpn_account_status(
                    vpn_client, vpn_account["ID"], 0
                )
                print("Fetching New Account And Reconnecting")
                self.connect_vpn(vpn_client, vpn_file_name)
                break

            elif line_count >= 70:
                print(
                    "OVPN Connection Is Most Likely Stuck On Connecting With No Effective Logic To Analyze Results, "
                    "Raising Error"
                )
                raise TimeoutError("VPN Connection Most Likely Stuck ON Loop")
        if not self.is_vpn_connected:
            print(
                "VPN Could Not Prove Connected For Some Other Reason, Switching VPN File And Reconnecting"
            )
            time.sleep(0.8)
            self.improvised_public_ip = True
            config_file = utils.fetch_random_file_name_from_directory(
                config_dir, "ovpn"
            )
            self.connect_vpn(
                vpn_client,
                config_file,
                id=vpn_account["ID"],
                username=vpn_account["USERNAME"],
                password=vpn_account["PASSWORD"],
            )
            return False
        else:
            return True
