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
    def __init__(self, id=None, device_type="", hardware="", user_agent_os="", platform="",
                 canvas_fp_offset=None, audio_context_fp_offset=None, font_fp_offset=None, webgl_fp_offset=None,
                 hardware_concurrency=None, memory=None, has_mouse=None, has_battery=None, has_touch=None,
                 browser_name="", browser_version="", screen_resolution=None, gpu_vendor="", gpu_renderer="",
                 proxy_client="", proxy_geo="", referer="", reading_speed=None, timezone=None,
                 mouse_delta_y=None, ad_click_probability=0.2, ad_keywords=None, ad_keywords_click_probability=0.2,
                 cookies=list()):
        self.identity_raw = None
        self.id = id
        self.device_type = device_type
        self.hardware = hardware
        self.user_agent_os = user_agent_os
        self.platform = platform
        self.canvas_fp_offset = canvas_fp_offset
        self.audio_context_fp_offset = audio_context_fp_offset
        self.font_fp_offset = font_fp_offset
        self.webgl_fp_offset = webgl_fp_offset
        self.hardware_concurrency = hardware_concurrency
        self.memory = memory
        self.has_mouse = has_mouse
        self.has_battery = has_battery
        self.has_touch = has_touch
        self.browser_name = browser_name
        self.browser_version = browser_version
        self.screen_resolution = screen_resolution
        if isinstance(screen_resolution, list):
            self.screen_width = screen_resolution[0]
            self.screen_height = screen_resolution[1]
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
        self.mouse_delta_y = mouse_delta_y
        self.cookies = cookies
        self.improvised_public_ip = True
        self.has_visited_today = 0
        self.page_depth = 0.3
        self.ad_click_probability = ad_click_probability
        self.ad_keywords = ad_keywords
        self.ad_keywords_click_probability = ad_keywords_click_probability

        self.data_controller = DataController()

        self.is_vpn_connected = True
        self.article_read_time_offset = random.randint(-15, 12)

    def resolve_identity_from_cloud(self, method, value):
        identity = self.data_controller.fetch_an_identity(method, value)
        if not identity:
            raise ValueError("Identity Fetched Does Not Appear To Be What It Is, Something Has To Be Wrong With Given"
                             "Parameters")
        print("Successfully Fetched An Identity With ID:", identity["ID"])
        print("Resolving Details To Identity Object")
        self.id = identity["ID"]
        self.device_type = identity["DEVICE_TYPE"]
        self.hardware = identity["HARDWARE"]
        self.user_agent_os = identity["UA_OS"]
        self.platform = identity["PLATFORM"]
        identity["CANVAS_FP_OFFSET"] = json.loads(identity["CANVAS_FP_OFFSET"])
        self.canvas_fp_offset = identity["CANVAS_FP_OFFSET"]
        self.audio_context_fp_offset = identity["AUDIO_CONTEXT_FP_OFFSET"]
        identity["FONT_FP_OFFSET"] = json.loads(identity["FONT_FP_OFFSET"])
        self.font_fp_offset = identity["FONT_FP_OFFSET"]
        identity["WEBGL_FP_OFFSET"] = json.loads(identity["WEBGL_FP_OFFSET"])
        self.webgl_fp_offset = identity["WEBGL_FP_OFFSET"]
        self.hardware_concurrency = identity["HARDWARE_CONCURRENCY"]
        self.memory = identity["MEMORY"]
        self.has_mouse = identity["HAS_MOUSE"]
        self.has_battery = identity["HAS_BATTERY"]
        self.has_touch = identity["HAS_TOUCH"]
        self.browser_name = identity["BROWSER"]
        identity["BROWSER_VERSION"] = json.loads(identity["BROWSER_VERSION"].replace("'", "\""))
        self.browser_version = identity["BROWSER_VERSION"]
        identity["SCREEN_RESOLUTION"] = json.loads(identity["SCREEN_RESOLUTION"])
        self.screen_resolution = identity["SCREEN_RESOLUTION"]
        if isinstance(self.screen_resolution, list):
            self.screen_width = self.screen_resolution[0]
            self.screen_height = self.screen_resolution[1]
        else:
            self.screen_width = 1920
            self.screen_height = 1080
        self.gpu_vendor = identity["GPU_VENDOR"]
        self.gpu_renderer = identity["GPU_RENDERER"]
        self.proxy_client = identity["PROXY_CLIENT"]
        self.proxy_geo = identity["PROXY_GEO"]
        identity["REFERRALS"] = json.loads(identity["REFERRALS"].replace("'", "\""))
        self.referrals = identity["REFERRALS"]
        self.referer = None
        self.reading_speed = identity["READING_SPEED"]
        self.user_agent = None
        self.mouse_delta_y = identity["MOUSE_DELTA_Y"]
        self.has_visited_today = identity["HAS_VISITED_TODAY"]
        self.page_depth = identity["PAGE_DEPTH"]
        try:
            if identity["COOKIES"]:
                if identity["COOKIES"][-3:] != '"}]':
                    self.cookies = json.loads(identity["COOKIES"] + "\"}]")
                else:
                    self.cookies = json.loads(identity["COOKIES"])
        except json.JSONDecodeError:
            if isinstance(identity["COOKIES"], list):
                self.cookies = identity["COOKIES"]
            else:
                self.cookies = list()
        self.ad_click_probability = identity["AD_CLICK_PROBABILITY"]
        self.ad_keywords = identity["AD_KEYWORDS"]
        self.ad_keywords_click_probability = identity["AD_KEYWORDS_CLICK_PROBABILITY"]
        self.identity_raw = identity

    def auto_initiate_identity(self, method, method_value):
        self.resolve_identity_from_cloud(method, method_value)
        self.resolve_user_agent(self.browser_name, self.user_agent_os, self.browser_version)
        self.resolve_timezone()
        # self.connect_vpn(self.vpn_client, self.ovpn_file_name)
        self.resolve_referer()

    def resolve_timezone(self):
        if self.improvised_public_ip:
            geolocation = self.data_controller.fetch_geolocation_data(self.resolve_proxy_url(self.proxy_geo, self.proxy_client))

            self.timezone = [geolocation["timezone"], geolocation["offset"] / 60, geolocation["continent"] + " " +
                             geolocation["city"] + " Standard Time"]
        elif self.identity_raw["TIMEZONE_ID"]:
            self.timezone = [self.identity_raw["TIMEZONE_ID"], self.identity_raw["TIMEZONE_OFFSET"],
                             self.identity_raw["TIMEZONE_FULL_NAME"]]
        else:
            print("Resolving Timezone From Cloud")
            identity_timezone = self.data_controller.fetch_timezone(self.id, self.resolve_proxy_url(self.proxy_geo, self.proxy_client))
            self.timezone = [identity_timezone["TIMEZONE_ID"], identity_timezone["TIMEZONE_OFFSET"],
                             identity_timezone["TIMEZONE_FULL_NAME"]]
            print("geo location: ", identity_timezone)
            print("Successfully Resolved Timezone")

    def resolve_referer(self):
        self.referer = random.choice(self.referrals)

    def update_cookies(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        self.data_controller.update_cookies(self.id, cookies)

    def fetch_referrer(self):
        return self.identity.referrals[random.randint(0, len(self.identity.referrals) - 1)]

    def resolve_user_agent(self, browser_name, user_agent_os, browser_version):
        browser_version = [str(version) for version in browser_version]
        chrome_template = "Mozilla/5.0 (user_agent_os) AppleWebKit/awv1 (KHTML, like Gecko) Chrome/cv2 Safari/sv3"
        if self.device_type == "is_smartphone":
            chrome_template = "Mozilla/5.0 (user_agent_os) AppleWebKit/awv1 (KHTML, like Gecko) Chrome/cv2 Mobile Safari/sv3"
        if user_agent_os.find("iPhone") >= 1:
            chrome_template = "Mozilla/5.0 (user_agent_os) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/cv2 Mobile/15E148 Safari/604.1"
        if browser_name == "chrome" and isinstance(user_agent_os, str) and isinstance(browser_version, list):
            chrome_ua = chrome_template.replace("user_agent_os", user_agent_os)
            chrome_ua = chrome_ua.replace("awv1", browser_version[0])
            chrome_ua = chrome_ua.replace("cv2", browser_version[1])
            chrome_ua = chrome_ua.replace("sv3", browser_version[2])
            self.user_agent = chrome_ua
            print("Successfully Resolved User Agent")
        else:
            print(
                "Potential Error: No User Agent Refactor Option Was Created For This Browser, Please Resolve As Quickly"
                " As Possible")
            return None

    def disconnect_all_vpn(self):
        if Identity.ovpn_process is not None:
            print("Closing Program Openvpn Connection")
            Identity.ovpn_process.kill()
            self.is_vpn_connected = False
        else:
            print("Closing All Existing Openvpn Connections")
            ovpn_kill_command = 'sudo killall openvpn'
            try:
                ovpn_kill_process = subprocess.Popen(ovpn_kill_command.split(), stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE)
                ovpn_kill_process.wait(10)
                self.is_vpn_connected = False
            except:
                pass

    def generate_unique_lowercase_numbers_characters(self, length=12):
        chars = string.ascii_lowercase + string.digits
        random.seed()
        return ''.join(random.choice(chars) for _ in range(length))

    def resolve_proxy_url(self, geo_target, proxy_name="smartproxy.com"):
        if proxy_name == "smartproxy.com":
            if geo_target:
                proxy_url = bot_constants.PROXY_STICKY_TEMPLATE.replace("<geo_target_area>", bot_constants.PROXY_GEO_TARGET_AREA)
                proxy_url = proxy_url.replace("<port>", str(bot_constants.PROXY_PORT))
                proxy_url = proxy_url.replace("<user>", bot_constants.PROXY_USERNAME)
                proxy_url = proxy_url.replace("<geo_target>", geo_target)
                proxy_url = proxy_url.replace("<ss_duration>", str(bot_constants.PROXY_SESSION_DURATION))
                proxy_url = proxy_url.replace("<ss_string>", self.generate_unique_lowercase_numbers_characters())
                proxy_url = proxy_url.replace("<pass>", bot_constants.PROXY_PASSWORD)
                return proxy_url
            else:
                return bot_constants.PROXY_RANDOM_TEMPLATE
        return False

    def connect_vpn(self, vpn_client, vpn_file_name, **kwargs):
        if "id" in kwargs.keys() and "username" in kwargs.keys() and "password" in kwargs.keys():
            vpn_account = {"ID": kwargs["id"], "USERNAME": kwargs["username"], "PASSWORD": kwargs["password"]}
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

        bash_command = f"sudo openvpn --config {config_dir + vpn_file_name}" \
                       f" --auth-user-pass {bot_constants.FULL_DIRECTORY_PATH}/identity/account_details.temp.conf " \
                       f"--auth-nocache --server-poll-timeout {bot_constants.OVPN_MAX_WAIT_TIME_TILL_IP_IMPROVISE}"

        temp_acc_file = open(f"{bot_constants.FULL_DIRECTORY_PATH}/identity/account_details.temp.conf", "w")
        temp_acc_file.write(vpn_account["USERNAME"] + "\n" + vpn_account["PASSWORD"])
        temp_acc_file.close()
        print(f"Connecting To OpenVPN({vpn_client}) Server On File: {vpn_file_name}")
        Identity.ovpn_process = subprocess.Popen("exec "+bash_command, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, shell=True)

        line_count = 0
        for line in Identity.ovpn_process.stdout:
            line = line.decode()
            line_count += 1
            if "AUTH_FAILED" in line:
                print("Account Details Seems To Be Ineffective --> id, username, password", vpn_account["ID"],
                      vpn_account["USERNAME"], vpn_account["PASSWORD"])
                retries_left = bot_constants.MAX_OVPN_CONNECT_RETRIES
                if "retries_left" in kwargs.keys():
                    retries_left = kwargs["retries_left"]
                if retries_left > 0:
                    print("Retrying Account, Retries Left --> ", retries_left)
                    retries_left -= 1
                    self.connect_vpn(vpn_client, vpn_file_name, id=vpn_account["ID"], username=vpn_account["USERNAME"],
                                     password=vpn_account["PASSWORD"], retries_left=retries_left)
                else:
                    self.data_controller.update_vpn_account_status(vpn_client, vpn_account["ID"], 0)
                    print("Fetching New Account And Reconnecting")
                    self.connect_vpn(vpn_client, vpn_file_name)
                    break
            elif "Initialization Sequence Completed" in line:
                print("Account Details Valid, Connected Successfully : id, username, password -->", vpn_account["ID"],
                      vpn_account["USERNAME"], vpn_account["PASSWORD"])
                self.data_controller.update_vpn_account_status(vpn_client, vpn_account["ID"], 1)
                self.is_vpn_connected = True
                break
            elif "Connection timed out" in line or "connection failed" in line or "connection-reset" in line:
                print("OVPN Seems To Be Stuck Connecting, Most Probably A Dead OVPN Config File, Less Likely Internet "
                      "Issues(Check To Make Sure). Improvising New Ip Address Via Another OVPN Config File")
                self.improvised_public_ip = True
                config_file = utils.fetch_random_file_name_from_directory(config_dir, "ovpn")
                self.connect_vpn(vpn_client, config_file, id=vpn_account["ID"], username=vpn_account["USERNAME"],
                                 password=vpn_account["PASSWORD"])
                break

            elif "Enter Auth" in line:
                print("No Potential Username And/Or Password Found In Configuration")
                self.data_controller.update_vpn_account_status(vpn_client, vpn_account["ID"], 0)
                print("Fetching New Account And Reconnecting")
                self.connect_vpn(vpn_client, vpn_file_name)
                break

            elif line_count >= 70:
                print("OVPN Connection Is Most Likely Stuck On Connecting With No Effective Logic To Analyze Results, "
                      "Raising Error")
                raise TimeoutError("VPN Connection Most Likely Stuck ON Loop")
        if not self.is_vpn_connected:
            print("VPN Could Not Prove Connected For Some Other Reason, Switching VPN File And Reconnecting")
            time.sleep(0.8)
            self.improvised_public_ip = True
            config_file = utils.fetch_random_file_name_from_directory(config_dir, "ovpn")
            self.connect_vpn(vpn_client, config_file, id=vpn_account["ID"], username=vpn_account["USERNAME"],
                             password=vpn_account["PASSWORD"])
            return False
        else:
            return True
