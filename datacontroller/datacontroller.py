import json
import requests

from constants.config import DEBUG
from constants.bot_constants import IDENTITY_API_BASE_HOST

from exceptions.identity import TimezoneFetchException


class DataController:
    server_addr = IDENTITY_API_BASE_HOST
    timeout = 12

    def __init__(self):
        pass

    async def fetch_an_identity(self, method, value):
        if isinstance(value, list):
            value = json.dumps(value)
        req_url = f"bots/identity/{method}/{value}/"
        if method == "random":
            req_url = f"bots/identity/random/"
        identity = requests.get(
            self.server_addr + req_url,
            timeout=DataController.timeout,
            verify=False,
        )
        identity.close()
        if identity.text == "void":
            return False
        return identity.json()

    async def fetch_timezone(self, identity_id: int, proxy=None, retries=0):
        # try:
        req_url = f"bots/identity/{identity_id}/timezone/"
        req_session = requests.session()
        identity_id = str(identity_id)
        if proxy:
            req_session.proxies = {
                "http": "http://" + proxy,
                "https": "http://" + proxy,
                "no_proxy": "localhost,127.0.0.1",
            }
        identity_timezone = req_session.get(
            self.server_addr + req_url,
            timeout=DataController.timeout,
            verify=not DEBUG,
        )
        identity_timezone.close()
        if identity_timezone.status_code == 407:
            print("Invalid Proxy Credentials, Exiting....")
            exit()
        if identity_timezone.ok:
            return identity_timezone.json()
        else:
            raise TimezoneFetchException

    async def fetch_geolocation_data(self, proxy=None):
        try:
            api_endpoint = "http://ip-api.com/json?fields=34652445"
            req_session = requests.session(verify=not DEBUG)
            if proxy:
                req_session.proxies = {
                    "http": "http://" + proxy,
                    "https": "https://" + proxy,
                }
            ip_geolocation = req_session.get(
                api_endpoint, timeout=DataController.timeout
            )
            if "Proxy Not Found" in ip_geolocation.text:
                return False
            else:
                return ip_geolocation.json()
        except:
            return False

    async def identity_visited_webpage(self, identity_id, page_id):
        pass

    async def update_cookies(self, identity_id, cookies):
        req_url = f"bots/identity/{identity_id}/cookies/"
        cookies_update = requests.put(
            self.server_addr + req_url,
            json=cookies,
            timeout=DataController.timeout,
            verify=not DEBUG,
        )
        print("cookie update: " + cookies_update.text)
        cookies_update.close()

    @staticmethod
    async def fetch_active_random_url():
        req_url = "url/random/"
        page_details = requests.get(
            DataController.server_addr + req_url,
            timeout=DataController.timeout,
            verify=not DEBUG,
        )
        return page_details.json()

    @staticmethod
    async def ping_is_alive(bot_server_id):
        req_url = "bot_is_alive.php?bot_id=" + bot_server_id
        requests.get(DataController.server_addr + req_url)
