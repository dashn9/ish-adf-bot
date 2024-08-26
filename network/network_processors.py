import asyncio
import re
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from requests.exceptions import SSLError, ProxyError
from nodriver import cdp

from aiohttp_client_cache import CachedSession, SQLiteBackend, CachedResponse
from bots.devtools import devtools_primary

from bots import utils
from constants import bot_constants
from identity.client import Identity
from constants import config


class NetworkRunner:
    def __init__(self, bot_process_id, identity: Identity, use_proxy=False):
        self.identity = identity
        self.referer_use_times = 0
        self.total_request_size = 0
        self.bot_process_id = bot_process_id
        self.un_cached_response_size = 0
        self.cached_response_size = 0
        self.url_through_proxy_response_size = 0
        self.urls_through_proxy = set()
        self.proxy = None

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

    @asynccontextmanager
    # TODO: Disable caching
    async def proxy_cached_session(self):
        async with CachedSession(
            cache=SQLiteBackend(
                bot_constants.FULL_DIRECTORY_PATH
                + "/data/cache/request_cache/proxy_requests_cache"
            ),
            proxy=self.proxy,
        ) as session:
            yield session

    async def release_proxies(self):
        # release Proxyrack sticky session
        if self.identity.proxy_release_url:
            print(f"Bot Process Id {self.bot_process_id} <:::> Releasing proxy session")
            async with self.proxy_cached_session() as session:
                print(  # add to config,
                    await session.request(
                        url=self.identity.proxy_release_url,
                        method="GET",
                        proxies=self.proxy,
                    ).json()
                )

    async def inject_referer_into_header(self, request: cdp.network.Request):
        if self.referer_use_times < 1:
            request.headers["Referer"] = self.identity.referer
            # self.referer_use_times += 1

    async def track_request_size(self, request: cdp.network.Request):
        request_size = len(request.post_data or "") / 1024
        self.total_request_size += request_size

    async def print_total_usage(self):
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

    async def track_response_size(self, request: cdp.network.Request, response):
        if request.url in self.urls_through_proxy:
            self.url_through_proxy_response_size += len(response.content or "") / 1024
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

    async def response_interceptor(
        self, request: cdp.network.Request, response: CachedResponse
    ):
        self.track_response_size(request, response)
        if config.PRINT_NETWORK:
            print(f"Response url: {request.url}[{response.status_code}]")
            self.print_total_usage()

        self.inject_js_to_spoof_fingerprintable_objects_on_website_server_response(
            request, response
        )

    async def inject_js_to_spoof_fingerprintable_objects_on_website_server_response(
        self, request: cdp.network.Response, response: CachedResponse
    ):
        """
        A Method
        :param: The Orginal Request
        :param response: The Response of The Web Server To Adjust Before Reaching Browser
        :return: True On Success, False On Failure
        """
        if response:
            body = await response.text()
            try:
                if (
                    (
                        response.headers.get("content-type").find("text/html")
                        or not re.search(r"(?<!https:)(?<!https:/)(\/\w)$", request.url)
                        or re.match(r"(.html|.htm)$", request.url)
                    )
                    and request.method == "GET"
                    and response.status == 200
                ):
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
                            browser_vendor=(
                                "Apple Computer, Inc."
                                if self.identity.browser_name == "safari"
                                else ""
                            ),
                            font_width_offset=self.identity.font_fp_offset[0],
                            font_height_offset=self.identity.font_fp_offset[1],
                            navigator_platform=self.identity.platform.get(
                                "navigator_platform", ""
                            ),
                            hardware_specs={
                                "hardware_concurrency": self.identity.hardware_concurrency,
                                "memory": self.identity.memory,
                            },
                            has_battery=has_battery,
                            referer=self.identity.referer,
                        )
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
                            return body
                return body
            except Exception:
                pass
            self.identity.referrer = ""
        return False

    async def request_interceptor(
        self, pausedRequest: cdp.fetch.RequestPaused, *args, **kwarg
    ):
        request = pausedRequest.request
        reqHost = urlparse(request.url).netloc

        async def network_through_proxy(
            generate_empty_response_on_fail=True, retries=0
        ):
            print(
                f"Bot Process Id {self.bot_process_id} <:::> {request.url} is passing through the proxy"
            )
            try:
                async with self.proxy_cached_session() as session:
                    async with session.request(
                        url=request.url,
                        headers=request.headers,
                        allow_redirects=False,
                        method=request.method,
                        data=request.post_data,
                    ) as response:
                        self.urls_through_proxy.add(request.url)
                        response_body = await self.inject_js_to_spoof_fingerprintable_objects_on_website_server_response(
                            request, response
                        )
                        asyncio.create_task(
                            devtools_primary.fulfill_request(
                                self.web_browser_driver,
                                pausedRequest.request_id,
                                response.status,
                                response_headers=[
                                    cdp.fetch.HeaderEntry(k, v)
                                    for k, v in response.headers.items()
                                ],
                                body=response_body.encode(),
                            )
                        )
                        return True
            except (SSLError, ProxyError):
                # fix against ip leaks
                if generate_empty_response_on_fail and retries < 1:
                    await asyncio.sleep(0.5)
                    return network_through_proxy(retries=retries + 1)
                else:
                    asyncio.create_task(
                        devtools_primary.continue_request(
                            self.web_browser_driver,
                            pausedRequest.request_id,
                            headers=[
                                cdp.fetch.HeaderEntry(k, v)
                                for k, v in request.headers.items()
                            ],
                        )
                    )
                    print(
                        f"Bot Process Id {self.bot_process_id} <:::> {request.url} generated an ssl or proxy error, "
                        f"it won't go through proxy, so dud response was generated"
                    )
                return False

        await self.track_request_size(request)
        if config.PRINT_NETWORK:
            print(f"Request url: {request.url}[{request.method}]")
            await self.print_total_usage()
        await self.inject_referer_into_header(request)
        if bot_constants.PROXY_WHITELISTED_DOMAINS == "*":
            if utils.url_ends_with(
                request, bot_constants.PROXY_BLACKLISTED_EXTENSIONS
            ) or utils.has_string_in(reqHost, bot_constants.PROXY_BLACKLISTED_DOMAINS):
                asyncio.create_task(
                    devtools_primary.continue_request(
                        self.web_browser_driver,
                        pausedRequest.request_id,
                        headers=[
                            cdp.fetch.HeaderEntry(k, v)
                            for k, v in request.headers.items()
                        ],
                    )
                )
            else:
                asyncio.create_task(network_through_proxy())
        # fetching driver.current_url while a page is loading posed some issues, you can find alternate ways to
        # implement the check of if current url equates browser active loading url
        elif not (
            (
                utils.has_string_in(
                    request.headers, bot_constants.PROXY_WHITELISTED_DOMAINS
                )
                and not utils.url_ends_with(
                    request.url, bot_constants.PROXY_BLACKLISTED_EXTENSIONS
                )
            )
            and not utils.has_string_in(
                reqHost, bot_constants.PROXY_BLACKLISTED_DOMAINS
            )
        ):
            asyncio.create_task(
                devtools_primary.continue_request(
                    self.web_browser_driver,
                    pausedRequest.request_id,
                    headers=[
                        cdp.fetch.HeaderEntry(k, v) for k, v in request.headers.items()
                    ],
                )
            )
        else:
            asyncio.create_task(network_through_proxy())
