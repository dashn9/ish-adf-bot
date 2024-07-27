import time
import re
import requests as main_requests
from requests.exceptions import SSLError, ProxyError

from seleniumwire.utils import decode
from seleniumwire.thirdparty.mitmproxy.net.http import encoding
from seleniumwire import request
import requests_cache

from bots import utils
from constants import bot_constants
from identity.client import Identity
from constants import config


class NetworkRunner:
    def __init__(self, bot_process_id, identity: Identity, use_proxy=False):
        self.cached_requests_session = requests_cache.CachedSession(
            bot_constants.FULL_DIRECTORY_PATH + "/caches/request_caches/requests_cache"
        )
        self.proxy_requests_session = requests_cache.CachedSession(
            bot_constants.FULL_DIRECTORY_PATH
            + "/caches/request_caches/proxy_requests_cache",
            cache_control=True,
        )

        self.identity = identity
        self.referer_use_times = 0
        self.total_request_size = 0
        self.bot_process_id = bot_process_id
        self.un_cached_response_size = 0
        self.cached_response_size = 0
        self.url_through_proxy_response_size = 0
        self.urls_cached = set()
        self.urls_through_proxy = set()

        if not config.PRINT_NETWORK:
            main_requests.packages.urllib3.disable_warnings()

        if use_proxy:
            self.proxy_url = self.identity.proxy_url
            self.proxy = {
                "http": "http://" + self.identity.proxy_url,
                "https": "http://" + self.identity.proxy_url,
                "no_proxy": "localhost,127.0.0.1",
            }
            print(
                f"Bot Process Id {self.bot_process_id} <:::> Adding a proxy option for this session on this proxy"
                f" path: {self.identity.proxy_url}"
            )
            self.proxy_requests_session.proxies = self.proxy

    def release_proxies(self):
        # release Proxyrack sticky session
        if self.identity.proxy_release_url:
            print(f"Bot Process Id {self.bot_process_id} <:::> Releasing proxy session")
            try:
                print(  # add to config,
                    main_requests.request(
                        url=self.identity.proxy_release_url,
                        method="GET",
                        proxies=self.proxy,
                    ).json()
                )
            except:
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> An error occurred, might have failed to release"
                )

    def inject_referer_into_header(self, request: request.Request):
        if self.referer_use_times < 1:
            del request.headers["Referer"]
            request.headers.add_header("Referer", self.identity.referer)
            self.referer_use_times += 1

    def track_request_size(self, request):
        request_size = len(request.body or "") / 1024
        self.total_request_size += request_size

    def print_total_usage(self):
        print(
            f"Bot Process Id {self.bot_process_id} <:::> Total request size: {self.total_request_size:.2f} KB"
        )
        print(
            f"Bot Process Id {self.bot_process_id} <:::> Total un-cached response size: {self.un_cached_response_size:.2f} KB"
        )
        print(
            f"Bot Process Id {self.bot_process_id} <:::> Total proxy response size: {self.url_through_proxy_response_size:.2f} KB"
        )
        print(
            f"Bot Process Id {self.bot_process_id} <:::> Total cached response size: {self.cached_response_size:.2f} KB"
        )
        print(
            f"Bot Process Id {self.bot_process_id} <:::> Total data transferred: "
            f"{self.total_request_size + self.un_cached_response_size + self.url_through_proxy_response_size:.2f} KB"
        )

    def track_response_size(self, request, response):
        if request.url in self.urls_through_proxy:
            self.url_through_proxy_response_size += len(response.body or "") / 1024
            self.urls_through_proxy.remove(request.url)
        elif request.url not in self.urls_cached:
            self.un_cached_response_size += len(response.body or "") / 1024
        else:
            if config.PRINT_NETWORK:
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> {request.url} is cached"
                )
            self.urls_cached.remove(request.url)
            self.cached_response_size += len(response.body or "") / 1024

    def response_interceptor(
        self, request: request.Request, response: request.Response
    ):
        self.track_response_size(request, response)
        if config.PRINT_NETWORK:
            print(f"Response url: {request.url}[{response.status_code}]")
            self.print_total_usage()

        self.inject_js_to_spoof_fingerprintable_objects_on_website_server_response(
            request, response
        )

    def inject_js_to_spoof_fingerprintable_objects_on_website_server_response(
        self, request: request.Request, response: request.Response
    ):
        """
        A Method
        :param: The Orginal Request
        :param response: The Response of The Web Server To Adjust Before Reaching Browser
        :return: True On Success, False On Failure
        """
        if response:
            try:
                if (
                    (
                        response.headers.get("content-type").find("text/html")
                        or not re.search(r"(?<!https:)(?<!https:/)(\/\w)$", request.url)
                        or re.match(r"(.html|.htm)$", request.url)
                    )
                    and request.method == "GET"
                    and response.status_code == 200
                ):
                    body = decode(
                        response.body,
                        response.headers.get("Content-Encoding", "identity"),
                    )
                    body = body.decode("utf-8")
                    if (
                        body.find("<!DOCTYPE") == 0
                        or body.find("<html") == 0
                        or body.find("<!--") == 0
                    ):
                        if self.identity.has_battery == "has_battery":
                            has_battery = True
                        else:
                            has_battery = False
                        fingerprintables_spoof_code = utils.return_fingerprintables_spoof_js_code(
                            offset_color_value=tuple(self.identity.canvas_fp_offset),
                            audio_context_offset=self.identity.audio_context_fp_offset,
                            webgl_params=(
                                self.identity.gpu_vendor,
                                15,
                                12,
                                14,
                                14,
                                13,
                                4,
                                4,
                                4,
                                4,
                                3,
                                3,
                                3,
                                3,
                                6,
                                11,
                                12,
                                12,
                                self.identity.gpu_renderer,
                            ),
                            timezone=self.identity.timezone,
                            font_width_offset=self.identity.font_fp_offset[0],
                            font_height_offset=self.identity.font_fp_offset[1],
                            platform=self.identity.platform,
                            hardware_specs={
                                "hardware_concurrency": self.identity.hardware_concurrency,
                                "memory": self.identity.memory,
                            },
                            has_battery=has_battery,
                            referer=self.identity.referer,
                        )
                        self.identity.referer = ""
                        if isinstance(body, str):
                            if body.find("<head>") != -1:
                                body = utils.insert_text_into_string(
                                    body,
                                    "<script>"
                                    + fingerprintables_spoof_code
                                    + "</script>",
                                    "<head>",
                                    True,
                                )
                            else:
                                body = utils.insert_text_into_string_reg(
                                    body,
                                    fingerprintables_spoof_code,
                                    r"(<script>)|(<script .*?>)",
                                    True,
                                )
                            body = body.encode("utf-8")
                            body = encoding.encode(
                                body,
                                response.headers.get("Content-Encoding", "identity"),
                            )
                            if "content-length" in response.headers:
                                response.headers.replace_header(
                                    "content-length", str(len(body))
                                )
                            response.body = body
                            return True
            except Exception:
                pass
            self.identity.referrer = ""
        return False

    def terminate_unnecessary_requests(self, request):
        if request.url.endswith((".crx", "crx3")):
            request.abort()
            return True
        return False

    def request_interceptor(self, request: request.Request):
        if self.terminate_unnecessary_requests(request):
            return

        def network_through_no_proxy():
            try:
                response = self.cached_requests_session.request(
                    url=request.url,
                    verify=False,
                    headers=request.headers,
                    allow_redirects=False,
                    method=request.method,
                    data=request.body,
                )
                if response.from_cache:
                    self.urls_cached.add(request.url)

                response.body = response.content
                request.response = response
                return True
            except SSLError:
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> {request.url} would not be able to go through the "
                    f"cacher as a result of an ssl error"
                )
                return False

        def network_through_proxy(generate_empty_response_on_fail=True, retries=0):
            print(
                f"Bot Process Id {self.bot_process_id} <:::> {request.url} is passing through the proxy"
            )
            try:
                response = self.proxy_requests_session.request(
                    url=request.url,
                    verify=False,
                    headers=request.headers,
                    allow_redirects=False,
                    method=request.method,
                    data=request.body,
                )
                self.urls_through_proxy.add(request.url)
                response.body = response.content
                request.response = response
                return True
            except (SSLError, ProxyError):
                # fix against ip leaks
                if generate_empty_response_on_fail and retries < 1:
                    time.sleep(0.5)
                    return network_through_proxy(retries=retries + 1)
                else:
                    response = main_requests.Response()
                    response.status_code = 408
                    response._content = b""
                    response.body = response.content
                    request.response = response
                    print(
                        f"Bot Process Id {self.bot_process_id} <:::> {request.url} generated an ssl or proxy error, "
                        f"it won't go through proxy, so dud response was generated"
                    )
                return False

        self.track_request_size(request)
        if config.PRINT_NETWORK:
            print(f"Request url: {request.url}[{request.method}]")
            self.print_total_usage()
        self.inject_referer_into_header(request)
        if bot_constants.PROXY_WHITELISTED_DOMAINS == "*":
            if utils.url_ends_with(
                request.url, bot_constants.PROXY_BLACKLISTED_EXTENSIONS
            ) or utils.has_string_in(
                request.host, bot_constants.PROXY_BLACKLISTED_DOMAINS
            ):
                network_through_no_proxy()
            else:
                network_through_proxy()
        # fetching driver.current_url while a page is loading posed some issues, you can find alternate ways to
        # implement the check of if current url equates browser active loading url
        elif not (
            (
                utils.has_string_in(
                    request.host, bot_constants.PROXY_WHITELISTED_DOMAINS
                )
                and not utils.url_ends_with(
                    request.url, bot_constants.PROXY_BLACKLISTED_EXTENSIONS
                )
            )
            and not utils.has_string_in(
                request.host, bot_constants.PROXY_BLACKLISTED_DOMAINS
            )
        ):
            network_through_no_proxy()
        else:
            network_through_proxy()
