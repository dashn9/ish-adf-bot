import json
from numpy import identity
import requests

from constants.bot_constants import IDENTITY_API_BASE_HOST


class DataController:
    server_addr = IDENTITY_API_BASE_HOST
    timeout = 12

    def __init__(self):
        pass

    def fetch_an_identity(self, method, value):
        session = requests.session()
        if isinstance(value, list):
            value = json.dumps(value)
        req_url = f"bots/identity/{method}/{value}"
        identity = session.get(
            self.server_api + req_url, timeout=DataController.timeout
        )
        identity.close()
        if identity.text == "void":
            return False
        return identity.json()

    def fetch_timezone(self, identity_id, proxy=None, retries=0):
        try:
            session = requests.session()
            req_url = "fetch_update_timezone.php"
            if identity_id:
                identity_id = str(identity_id)
                req_url = req_url + "?id=" + identity_id
                if proxy:
                    session.proxies = {
                        "http": "http://" + proxy,
                        "https": "http://" + proxy,
                        "no_proxy": "localhost,127.0.0.1",
                    }
                identity_timezone = session.get(
                    "https://finnsec.us/api/" + req_url,
                    timeout=DataController.timeout,
                    verify=False,
                )
                # session.get("http://api.proxyrack.net/release")
                identity_timezone.close()
                return identity_timezone.json()
        except:
            if retries <= 2:
                retries += 1
                return self.fetch_timezone(identity_id, proxy, retries)

    def fetch_geolocation_data(self, proxy=None):
        try:
            session = requests.session()
            api_endpoint = "http://ip-api.com/json?fields=34652445"
            if proxy:
                session.proxies = {
                    "http": "http://" + proxy,
                    "https": "https://" + proxy,
                }
            ip_geolocation = session.get(api_endpoint, timeout=DataController.timeout)
            if "Proxy Not Found" in ip_geolocation.text:
                return False
            else:
                return ip_geolocation.json()
        except:
            return False

    def identity_visited_webpage(self, identity_id, page_id):
        pass

    def update_cookies(self, uid, cookies):
        session = requests.session()
        if isinstance(cookies, list):
            cookies = json.dumps(cookies)
        req_url = "update_cookies_for_identity.php"
        cookies_update = session.post(
            self.server_api + req_url,
            data={"identity_id": str(uid), "cookies": cookies},
            timeout=DataController.timeout,
        )
        print("cookie update: " + cookies_update.text)
        cookies_update.close()

    def fetch_vpn_account_details(self, vpn_client):
        session = requests.session()
        req_url = "get_a_vpn_account.php?vpn_client=" + vpn_client
        vpn_account = session.get(
            self.server_api + req_url, timeout=DataController.timeout
        )
        vpn_account.close()
        return vpn_account.json()

    def update_vpn_account_status(self, vpn_client, vpn_account_id, vpn_account_status):
        session = requests.session()
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
        vpn_account_update = session.get(
            self.server_api + req_url, timeout=DataController.timeout
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
    def fetch_active_random_url():
        session = requests.session()
        req_url = "fetch_active_urls.php?amount=rand"
        page_details = session.get(
            DataController.server_api + req_url, timeout=DataController.timeout
        )
        return page_details.text

    @staticmethod
    def ping_is_alive(bot_server_id):
        req_url = "bot_is_alive.php?bot_id=" + bot_server_id
        requests.get(DataController.server_api + req_url)
