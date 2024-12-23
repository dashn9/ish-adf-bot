import asyncio
import fnmatch
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from nodriver import cdp, Tab

from aiohttp import ClientSession, ClientResponse
from aiohttp.client_exceptions import ClientConnectionError, ClientHttpProxyError
from bots.devtools import devtools_primary

from bots import utils
from constants import config, bot_constants, browser_constants
from identity.client import Identity


class NetworkRulesEvaluator:
    def __init__(self, rules, default_aciton="browser"):
        self.rules = rules
        self.default_action = default_aciton
        self.request_counts = {}

    def match_rule(self, host, url, mime_type, tab_url, tab_creation_index):
        """Match the host and evaluate its rules."""
        host_rules = self.rules.get(host, self.rules.get("*", []))
        if not host_rules:
            return self.default_action

        action = None
        for rule in host_rules:
            result = self.evaluate_rule(
                rule, host, url, mime_type, tab_url, tab_creation_index
            )
            if result is not None:
                if result[1]:
                    return result[0]
                else:
                    action = result[0]

        return action or self.default_action

    def evaluate_rule(self, rule, host, url, mime_type, tab_url, tab_creaton_index):
        """Evaluate a single rule's conditions."""
        parsed_tab_url = urlparse(tab_url)
        condition = rule.get("condition", {})
        passed = True
        # MIME matching
        if "mime" in condition and not self.matches_condition(
            condition["mime"], mime_type
        ):
            passed = False

        # URL matching
        elif "url" in condition and not self.matches_condition(condition["url"], url):
            passed = False

        # tab_url_host is mostly experimental because it's sort of a pain to get the tab url especially if it's loading
        elif "tab_url_host" in condition and not self.matches_condition(
            condition["tab_url_host"], parsed_tab_url.netloc
        ):
            passed = False

        elif (
            "tab_creation_index" in condition
            and tab_creaton_index != condition["tab_creation_index"]
        ):
            passed = False

        # Reason for if and not elif, is so request_counts would be updated
        if "max_requests" in condition and condition["max_requests"] >= 0:
            count = self.request_counts.get(parsed_tab_url.netloc, 0)
            if count >= condition["max_requests"]:
                passed = False
            self.request_counts[parsed_tab_url.netloc] = count + 1
        if passed:
            return (rule["action"], True)  # All conditions passed
        return (rule.get("fail_action", self.default_action), False)

    @staticmethod
    def matches_condition(condition, value):
        """Check if a value matches a condition with optional negation."""
        if isinstance(condition, str):
            condition = [condition]  # Normalize to list if a single string
        matches = False
        is_negated = False
        for pattern in condition:
            is_negated = pattern.startswith("!")
            clean_pattern = pattern[1:] if is_negated else pattern
            if fnmatch.fnmatch(value, clean_pattern):
                matches = True
                break
            else:
                matches = False
        if is_negated:
            matches = not matches

        return matches


class NetworkRunner:
    def __init__(self, bot_process_id, identity: Identity, use_proxy=False):
        self.identity = identity
        self.referrer_use_times = 0
        self.total_request_size = 0
        self.bot_process_id = bot_process_id
        self.un_cached_response_size = 0
        self.cached_response_size = 0
        self.url_through_proxy_response_size = 0
        self.urls_through_proxy = set()
        self.proxy = None

        if use_proxy:
            self.proxy_url = getattr(
                self.identity, "country_proxy_url", self.identity.proxy_url
            )
            self.proxy = "http://" + self.proxy_url
            print(
                f"Bot Process Id {self.bot_process_id} <:::> Adding a proxy option for this session on this proxy"
                f" path: {self.proxy_url}"
            )

    @asynccontextmanager
    # TODO: Disable caching
    async def proxy_session(self):
        async with ClientSession() as session:
            yield session

    async def release_proxies(self):
        # release Proxyrack sticky session
        if self.identity.proxy_release_url:
            print(f"Bot Process Id {self.bot_process_id} <:::> Releasing proxy session")
            async with self.proxy_session() as session:
                print(  # add to config,
                    await session.request(
                        url=self.identity.proxy_release_url,
                        method="GET",
                    ).json()
                )

    async def inject_referrer_into_header(self, request: cdp.network.Request):
        if self.referrer_use_times < 1:
            request.headers["referrer"] = self.identity.referrer
            self.referrer_use_times += 1

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
        self, request: cdp.network.Request, response: ClientResponse
    ):
        self.track_response_size(request, response)
        if config.PRINT_NETWORK:
            print(f"Response url: {request.url}[{response.status_code}]")

    async def strip_chromium_headers(self, headers):
        # fufill_request works in an unusual behaviour, it only responds to sec-ch headers
        new_headers = {}
        for key, value in headers.items():
            if key not in browser_constants.CHROMIUM_SPECIFIC_HEADERS:
                new_headers[key] = value
        return new_headers

    async def conform_headers_according_to_browser(self, headers: list):
        # If identityself.default_actionis not chromium
        if (
            self.identity.browser_name not in ["edge", "chrome"]
            or self.identity.os == "iOS"
        ):
            return await self.strip_chromium_headers(headers)
        return headers

    async def network_through_browser(self, target_tab, pausedRequest):
        request = pausedRequest.request
        asyncio.create_task(
            devtools_primary.continue_request(
                target_tab,
                pausedRequest.request_id,
                pausedRequest.frame_id,
                headers=[
                    cdp.fetch.HeaderEntry(k, str(v))
                    for k, v in (
                        await self.conform_headers_according_to_browser(
                            request.headers.to_json()
                        )
                    ).items()
                ],
            )
        )

    async def network_through_proxy(
        self,
        pausedRequest: cdp.fetch.RequestPaused,
        target_tab,
        generate_empty_response_on_fail=True,
        retries=0,
        failed_loading_requests=[],
    ):
        request = pausedRequest.request
        print(
            f"Bot Process Id {self.bot_process_id} <:::> {pausedRequest.frame_id}: {request.url} is passing through the proxy [{pausedRequest.resource_type}]"
        )
        try:
            async with self.proxy_session() as session:
                async with session.request(
                    url=request.url,
                    headers=await self.conform_headers_according_to_browser(
                        request.headers
                    ),
                    allow_redirects=False,
                    method=request.method,
                    data=request.post_data,
                    proxy=self.proxy,
                ) as response:
                    self.urls_through_proxy.add(request.url)
                    if pausedRequest.network_id not in failed_loading_requests:
                        asyncio.create_task(
                            devtools_primary.fulfill_request(
                                target_tab,
                                pausedRequest.request_id,
                                pausedRequest.frame_id,
                                response.status,
                                response_headers=[
                                    cdp.fetch.HeaderEntry(k, str(v))
                                    for k, v in response.headers.items()
                                ],
                                body=(await response.read()),
                            )
                        )
                    return True
        except ClientHttpProxyError as e:
            if e.code == 407:
                # Configure notification to admin
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> Invalid Proxy Credentials, Exiting to avoid getting burnt"
                )
                asyncio.get_event_loop().stop()
                exit()
            # fix against ip leaks
            if generate_empty_response_on_fail and retries < 1:
                await asyncio.sleep(0.5)
                asyncio.create_task(
                    self.network_through_proxy(
                        pausedRequest,
                        target_tab,
                        generate_empty_response_on_fail,
                        retries=retries + 1,
                        failed_loading_requests=failed_loading_requests,
                    )
                )
            else:
                if pausedRequest.network_id not in failed_loading_requests:
                    asyncio.create_task(
                        devtools_primary.fail_request(
                            target_tab,
                            request_id=pausedRequest.request_id,
                            frame_id=pausedRequest.frame_id,
                        )
                    )
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> {request.url} generated an ssl or proxy error, "
                    f"it won't go through proxy, so it was failed"
                )
            return False
        except ClientConnectionError as e:
            if pausedRequest.network_id not in failed_loading_requests:
                asyncio.create_task(
                    devtools_primary.fail_request(
                        target_tab,
                        request_id=pausedRequest.request_id,
                        frame_id=pausedRequest.frame_id,
                    )
                )
            print(
                f"Bot Process Id {self.bot_process_id} <:::> {request.url} did not connect"
            )

    async def request_interceptor(
        self, target_tab: Tab, rules: dict, tab_creation_index=-1
    ):
        await devtools_primary.enable_network(target_tab)
        failed_loading_requests = []
        network_rules = NetworkRulesEvaluator(rules)
        # The first tab would always have a url of chrome://newtab/, the second one would always have the first loaded url, which is mostly thanks to the extension that blocks the first
        # request of a tab giving enough time to fetch the url otherwise would have been about:blank
        tab_url = target_tab.target.url

        async def handle_failed_loading_request(failed_request, *args, **kwargs):
            failed_loading_requests.append(failed_request.request_id)

        await devtools_primary.listen_to_failed_loading_requests(
            target_tab, handle_failed_loading_request
        )

        async def interceptor(pausedRequest: cdp.fetch.RequestPaused, *args, **kwarg):
            request = pausedRequest.request
            req = urlparse(request.url)
            # Not intercepted at request level
            if (
                pausedRequest.response_error_reason
                or pausedRequest.response_status_code
            ):
                return False

            await self.track_request_size(request)
            if config.PRINT_NETWORK:
                print(f"Request url: {request.url}[{request.method}]")

            request_first_mime = request.headers.get("Accept", "*/*").split(",")[0]
            await self.inject_referrer_into_header(request)

            action = network_rules.match_rule(
                req.netloc, req.path, request_first_mime, tab_url, tab_creation_index
            )
            if action == "proxy":
                asyncio.create_task(
                    self.network_through_proxy(
                        pausedRequest,
                        target_tab,
                        failed_loading_requests=failed_loading_requests,
                    )
                )
            elif action == "browser":
                print(
                    f"Bot Process Id {self.bot_process_id} <:::> {pausedRequest.frame_id}: {request.url} is passing through the browser"
                )
                asyncio.create_task(
                    self.network_through_browser(target_tab, pausedRequest)
                )
            else:
                if pausedRequest.network_id not in failed_loading_requests:
                    asyncio.create_task(
                        devtools_primary.fail_request(
                            target_tab,
                            request_id=pausedRequest.request_id,
                            frame_id=pausedRequest.frame_id,
                        )
                    )

        return interceptor
