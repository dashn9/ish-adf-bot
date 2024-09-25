import base64
import re
import asyncio

from typing import Callable, Optional, List, Dict
from nodriver import Tab, cdp

from .. import utils


async def simulate_screen(tab: Tab, device_metrics: dict = {
        "width": 1366,
        "height": 768, "device_scale_factor": 2,
        "mobile": False
        }):
    await tab.send(cdp.emulation.set_device_metrics_override(
        position_x=0,
        position_y=0,
        width=device_metrics['width'], 
        height=device_metrics["height"], 
        device_scale_factor=device_metrics["device_scale_factor"],
        mobile=device_metrics["mobile"],
        ))
    
async def activate_mobile(
    tab: Tab, device_metrics: dict = {
        "width": 1366,
        "height": 768, "device_scale_factor": 2,
        "mobile": False
        }, 
    max_touch_points=5
):
    await simulate_screen(tab, device_metrics)
    await asyncio.sleep(0.5)
    await tab.send(cdp.emulation.set_touch_emulation_enabled(enabled=True, max_touch_points=max_touch_points))
    await asyncio.sleep(0.5)
    await tab.send(cdp.emulation.set_emit_touch_events_for_mouse(enabled=True))

async def listen_to_tab_creation(
        browser, tab_creation_callback: Callable[[cdp.fetch.RequestPaused], bool]
):
    browser.add_handler(cdp.target.TargetCreated, tab_creation_callback)

async def activate_all_focus(tab: Tab):
    await tab.send(cdp.emulation.set_focus_emulation_enabled(True))


async def change_user_agent(
    tab: Tab,
    user_agent,
    platform={
        "architecture": "",
        "bitness": "",
        "navigator_platform": "",
        "name": "",
        "version": "",
    },
    language=["en-US", "en"],
    browser="chrome",
    mobile=True,
    model="",
):
    brand = []
    full_version_list = []
    browser_version = ""
    def get_brands(chromium_version_fvi, chromium_version, browser_version_fvi, browser_version, browser_brand_name = "Google Chrome"):
        if int(chromium_version) < 128:
            return [
            {"brand": "Not)A;Brand", "version": "99"},
            {"brand": browser_brand_name, "version": browser_version},
            {"brand": "Chromium", "version": chromium_version},
        ], [
            {"brand": "Not)A;Brand", "version": "99.0.0.0"},
            {"brand": browser_brand_name, "version": browser_version_fvi},
            {"brand": "Chromium", "version": chromium_version_fvi},
        ]
        else: 
            return [
            {"brand": "Chromium", "version": chromium_version},
            {"brand": "Not;A=Brand", "version": "24"},
            {"brand": browser_brand_name, "version": browser_version},
        ],[
            {"brand": "Chromium", "version": chromium_version_fvi},
            {"brand": "Not;A=Brand", "version": "24.0.0.0"},
            {"brand": browser_brand_name, "version": browser_version_fvi},
        ]
    if browser == "chrome" and platform["name"] != "iOS":
        browser_version_fvi = re.search(r"Chrome/(\d+\.\d+\.\d+\.\d+)", user_agent).group(1)
        browser_version = browser_version_fvi.split(".")[0]
        brand, full_version_list = get_brands(browser_version_fvi, browser_version, browser_version_fvi, browser_version)
        user_agent = re.sub(
            r"Chrome/(\d+\.\d+\.\d*\.\d+)",  # Matches 1 to 4 parts in the version number
            lambda match: f"Chrome/{utils.normalize_version(match.group(1).split(".")[0])}",
            user_agent,
        )
        if int(browser_version) >= 110 and platform["name"] == "Android":
            user_agent = re.sub(r"\(.*?\)", "(Linux; Android 10; K)", user_agent, count=1)

    elif browser == "edge":
        browser_version_fvi = re.search(r"Edg/(\d+\.\d+\.\d+\.\d+)", user_agent).group(1)
        chromium_version_fvi = re.search(r"Chrome/(\d+\.\d+\.\d+\.\d+)", user_agent).group(
            1
        )
        chromium_version = chromium_version_fvi.split(".")[0]
        browser_version = browser_version_fvi.split(".")[0]
        brand, full_version_list = get_brands(chromium_version_fvi, chromium_version, browser_version_fvi, browser_version, "Microsoft Edge")
        user_agent = re.sub(
            r"(Edg|Chrome)/(\d+\.\d+\.\d*\.\d+)",  # Matches 1 to 4 parts in the version number
            lambda match: f"{match.group(1)}/{utils.normalize_version(match.group(2).split(".")[0])}",
            user_agent,
        )
    else:
        # Copy platform so as not to overwrite original value
        platform = platform.copy()
        # Reset platform to empty for none chromium browsers, like safari
        platform["name"] = ""
        platform["version"] = ""
        platform["architecture"] = ""
        platform["bitness"] = ""
        model = ""
        browser_version_fvi=None

    await tab.send(
        cdp.emulation.set_user_agent_override(
            user_agent=user_agent,
            accept_language=",".join(language),
            platform=platform["navigator_platform"] or "",
            user_agent_metadata=cdp.emulation.UserAgentMetadata(
                platform=platform["name"] or "",
                platform_version=platform["version"] or "",
                architecture=platform["architecture"] or "",
                model=model or "",
                mobile=mobile,
                brands=[
                    cdp.emulation.UserAgentBrandVersion.from_json(b) for b in brand
                ],
                full_version_list=[
                    cdp.emulation.UserAgentBrandVersion.from_json(full_version)
                    for full_version in full_version_list
                ],
                full_version=browser_version_fvi,
                bitness=platform["bitness"] or "",
                wow64=False,
            ),
        )
    )
    await tab.send(cdp.emulation.set_locale_override(language[0]))


async def set_hardware_concurrency(tab: Tab, hc=4):
    await tab.send(cdp.emulation.set_hardware_concurrency_override(hc))


async def set_timezone(tab: Tab, timezone="Etc/GMT"):
    await tab.send(cdp.emulation.set_timezone_override(timezone))


async def get_all_cookies(tab: Tab, with_local_storage=True):
    return await tab.cookies.get_all()


async def clear_all_cookies(tab: Tab):
    await tab.cookies.clear()


async def enable_network_interception(tab: Tab):
    await tab.send(cdp.fetch.enable())


async def disable_network_interception(tab: Tab):
    await tab.send(cdp.fetch.disable())

async def add_request_interception(
    tab: Tab, req_fufiller: Callable[[cdp.fetch.RequestPaused], bool]
):
    tab.add_handler(cdp.fetch.RequestPaused, req_fufiller)

async def get_response_body(
    tab: Tab, request_id: str
):
    await tab.send(cdp.fetch.get_response_body(request_id))


async def continue_request(
    tab: Tab,
    request_id: str,
    frame_id: cdp.page.FrameId,
    url: Optional[str] = None,
    method: Optional[str] = None,
    post_data: Optional[str] = None,
    headers: Optional[List[Dict[str, str]]] = None,
    intercept_response: Optional[bool] = None,
):
    await tab.send(
        cdp.fetch.continue_request(
            request_id=request_id,
            url=url,
            method=method,
            post_data=(base64.b64encode(post_data).decode() if post_data else None),
            headers=headers,
            intercept_response=intercept_response,
        )
    )


async def fulfill_request(
    tab: Tab,
    request_id: str,
    frame_id: cdp.page.FrameId,
    response_code: int,
    response_headers: Optional[List[Dict[str, str]]] = None,
    binary_response_headers: Optional[str] = None,
    body: Optional[str] = None,
    response_phrase: Optional[str] = None,
):
    await tab.send(
        cdp.fetch.fulfill_request(
            request_id=request_id,
            response_code=response_code,
            response_headers=response_headers,
            binary_response_headers=binary_response_headers,
            body=base64.b64encode(body).decode() if body else None,
            response_phrase=response_phrase,
        )
    )

async def fail_request(
        tab: Tab,
        request_id: str,
        frame_id: cdp.page.FrameId, 
        error_reason = cdp.network.ErrorReason.CONNECTION_ABORTED
):
    await tab.send(cdp.fetch.fail_request(request_id, error_reason))

async def set_all_cookies(tab: Tab, cookies):
    await tab.connection.send(cdp.storage.set_cookies([cdp.network.CookieParam.from_json(cookie) for cookie in cookies]))

async def stop_tab_loading(tab: Tab):
    await tab.send(cdp.page.stop_loading())

async def enable_network(tab: Tab):
    await tab.send(cdp.network.enable())

async def disable_network(tab: Tab):
    await tab.send(cdp.network.disable())

async def listen_to_failed_loading_requests(tab: Tab, failed_loading_request_handler: Callable[[cdp.fetch.RequestPaused], bool]):
    tab.add_handler(cdp.network.LoadingFailed, failed_loading_request_handler)

async def go_offline(tab: Tab):
    await tab.send(cdp.network.emulate_network_conditions(offline=True, latency=0, download_throughput=0, upload_throughput=0))

async def go_online(tab: Tab):
    await tab.send(cdp.network.emulate_network_conditions(offline=False, latency=0, download_throughput=-1, upload_throughput=-1))

async def enable_page(tab: Tab):
    await tab.send(cdp.page.enable())
    await tab.send(cdp.page.set_lifecycle_events_enabled(True))

async def listen_to_page_lifecycle(tab: Tab, page_lifecycle_handler: Callable[[cdp.fetch.RequestPaused], bool]):
    tab.add_handler(cdp.page.LifecycleEvent, page_lifecycle_handler)
