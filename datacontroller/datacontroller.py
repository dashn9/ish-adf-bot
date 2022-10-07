import json
import requests


class DataController:
    server_addr = "http://34.226.239.19/"
    server_api_addr = "http://34.226.239.19/api/"
    timeout = 12
    def __init__(self):
        self.server_addr = "http://34.226.239.19/"
        self.server_api_addr = "http://34.226.239.19/api/"

    def fetch_an_identity(self, method, value):
        if isinstance(value, list):
            value = json.dumps(value)
        req_url = f"get_a_bot_identity.php?method={method}&value={value}"
        identity = requests.get(self.server_api_addr + req_url, timeout=DataController.timeout)
        identity.close()
        if identity.text == "void":
            return False
        return identity.json()

    def fetch_timezone(self, identity_id):
        req_url = "fetch_update_timezone.php"
        if identity_id:
            identity_id = str(identity_id)
            req_url = req_url + "?id=" + identity_id
        identity_timezone = requests.get(self.server_api_addr + req_url, timeout=DataController.timeout)
        identity_timezone.close()
        return identity_timezone.json()

    def fetch_geolocation_data(self):
        api_endpoint = "http://ip-api.com/json?fields=34652445"
        ip_geolocation = requests.get(api_endpoint, timeout=DataController.timeout)
        return ip_geolocation.json()

    def identity_visited_webpage(self, identity_id, page_id):
        pass

    def update_cookies(self, uid, cookies):
        if isinstance(cookies, list):
            cookies = json.dumps(cookies)
        req_url = "update_cookies_for_identity.php?identity_id=" + str(uid) + "&cookies=" + cookies
        cookies_update = requests.get(self.server_api_addr + req_url, timeout=DataController.timeout)
        cookies_update.close()

    def fetch_vpn_account_details(self, vpn_client):
        req_url = "get_a_vpn_account.php?vpn_client="+vpn_client
        vpn_account = requests.get(self.server_api_addr+req_url, timeout=DataController.timeout)
        vpn_account.close()
        return vpn_account.json()

    def update_vpn_account_status(self, vpn_client, vpn_account_id, vpn_account_status):
        auth_status = "AUTH_VALID"
        vpn_account_id = str(vpn_account_id)
        if vpn_account_status == 0:
            auth_status = "AUTH_INVALID"
        req_url = "update_vpn_account.php?vpn_client=" + vpn_client +\
            "&account_id=" + vpn_account_id + "&account_status=" + auth_status
        vpn_account_update = requests.get(self.server_api_addr + req_url, timeout=DataController.timeout)
        vpn_account_update.close()
        if vpn_account_update.text == "successful":
            print(f"Successfully Updated {vpn_client} Account ID: {vpn_account_id}")
        else:
            print(f"Something Went Wrong While Updating {vpn_client} Account ID: {vpn_account_id}"
                  f", MESSAGE: {vpn_account_update.text}")

    @staticmethod
    def fetch_active_random_url():
        req_url = "fetch_active_urls.php?amount=rand"
        page_details = requests.get(DataController.server_api_addr + req_url, timeout=DataController.timeout)
        return page_details.text
