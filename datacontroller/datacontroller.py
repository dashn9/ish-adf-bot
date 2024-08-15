import json
import requests

from constants.config import DEBUG
from constants.bot_constants import IDENTITY_API_BASE_HOST


class DataController:
    server_addr = IDENTITY_API_BASE_HOST
    timeout = 12

    async def __init__(self):
        pass

    async def fetch_an_identity(self, method, value):
        if isinstance(value, list):
            value = json.dumps(value)
        req_url = f"bots/identity/{method}/{value}"
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
        req_url = f"bots/identity/{identity_id}/timezone/fetch"
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
        return identity_timezone.json()
        # except:
        #     if retries <= 2:
        #         retries += 1
        #         return self.fetch_timezone(identity_id, proxy, retries)

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

    async def update_cookies(self, uid, cookies):
        if isinstance(cookies, list):
            cookies = json.dumps(cookies)
        req_url = "update_cookies_for_identity.php"
        cookies_update = requests.post(
            self.server_addr + req_url,
            data={"identity_id": str(uid), "cookies": cookies},
            timeout=DataController.timeout,
            verify=not DEBUG,
        )
        print("cookie update: " + cookies_update.text)
        cookies_update.close()

    async def fetch_vpn_account_details(self, vpn_client):
        req_url = "get_a_vpn_account.php?vpn_client=" + vpn_client
        vpn_account = requests.get(
            self.server_addr + req_url, timeout=DataController.timeout
        )
        vpn_account.close()
        return vpn_account.json()

    async def update_vpn_account_status(
        self, vpn_client, vpn_account_id, vpn_account_status
    ):
        auth_status = "AUTH_VALID"
        vpn_account_id = str(vpn_account_id)
        if vpn_account_status == 0:
            auth_status = "AUTH_INVALID"
        req_url = (
            "update_vpn_account.php?vpn_client="
            + vpn_client
            + "&account_id="
            + vpn_account_id
            + "&account_status="
            + auth_status
        )
        vpn_account_update = requests.get(
            self.server_addr + req_url, timeout=DataController.timeout, verify=not DEBUG
        )
        vpn_account_update.close()
        if vpn_account_update.text == "successful":
            print(f"Successfully Updated {vpn_client} Account ID: {vpn_account_id}")
        else:
            print(
                f"Something Went Wrong While Updating {vpn_client} Account ID: {vpn_account_id}"
                f", MESSAGE: {vpn_account_update.text}"
            )

    @staticmethod
    async def fetch_active_random_url():
        req_url = "url/random"
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
