import base64
import re

from typing import Callable, Optional, List, Dict
from nodriver import Browser, cdp

from .. import utils


async def activate_mobile(
    web_driver: Browser, device_metrics: dict = {
        "width": 1366,
        "height": 768, "device_scale_factor": 2,
        "mobile": False
        }, 
    max_touch_points=5
):
    await web_driver.main_tab.send(cdp.emulation.set_device_metrics_override(
        position_x=0,
        position_y=0,
        width=device_metrics['width'], 
        height=device_metrics["height"], 
        device_scale_factor=device_metrics["device_scale_factor"],
        mobile=device_metrics["mobile"],
        # screen_orientation=cdp.emulation.ScreenOrientation(type_=device_metrics["screen_orientation"]["type"], angle=device_metrics["screen_orientation"]["angle"])
        )
        )
    await web_driver.main_tab.send(cdp.emulation.set_touch_emulation_enabled(enabled=True, max_touch_points=max_touch_points))
    await web_driver.main_tab.send(cdp.emulation.set_emit_touch_events_for_mouse(enabled=True))


async def activate_all_focus(web_driver: Browser):
    web_driver.execute_cdp_cmd("Emulation.setFocusEmulationEnabled", {"enabled": True})


async def change_user_agent(
    web_driver: Browser,
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
    if browser == "chrome":
        browser_version = re.search(r"Chrome/(\d+\.\d+\.\d+\.\d+)", user_agent).group(1)
        browser_version_fvi = browser_version.split(".")[0]
        brand = [
            {"brand": "Not)A;Brand", "version": "99"},
            {"brand": "Google Chrome", "version": browser_version_fvi},
            {"brand": "Chromium", "version": browser_version_fvi},
        ]
        full_version_list = [
            {"brand": "Not)A;Brand", "version": "99.0.0.0"},
            {"brand": "Google Chrome", "version": browser_version},
            {"brand": "Chromium", "version": browser_version},
        ]
        user_agent = re.sub(
            r"Chrome/(\d+\.\d+\.\d*\.\d+)",  # Matches 1 to 4 parts in the version number
            lambda match: f"Chrome/{utils.normalize_version(match.group(1).split(".")[0])}",
            user_agent,
        )
    elif browser == "edge":
        browser_version = re.search(r"Edg/(\d+\.\d+\.\d+\.\d+)", user_agent).group(1)
        chromium_version = re.search(r"Chrome/(\d+\.\d+\.\d+\.\d+)", user_agent).group(
            1
        )
        chromium_version_fvi = chromium_version.split(".")[0]
        browser_version_fvi = browser_version.split(".")[0]
        brand = [
            {"brand": "Chromium", "version": chromium_version_fvi},
            {"brand": "Not;A=Brand", "version": "24"},
            {"brand": "Microsoft Edge", "version": browser_version_fvi},
        ]
        full_version_list = [
            {"brand": "Chromium", "version": chromium_version},
            {"brand": "Not;A=Brand", "version": "24.0.0.0"},
            {"brand": "Microsoft Edge", "version": browser_version},
        ]
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

    await web_driver.main_tab.send(
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
                full_version=browser_version,
                bitness=platform["bitness"] or "",
                wow64=False,
            ),
        )
    )
    await web_driver.main_tab.send(cdp.emulation.set_locale_override(language[0]))


async def set_hardware_concurrency(web_driver: Browser, hc=4):
    await web_driver.main_tab.send(cdp.emulation.set_hardware_concurrency_override(hc))


async def set_timezone(web_driver: Browser, timezone="Etc/GMT"):
    await web_driver.main_tab.send(cdp.emulation.set_timezone_override(timezone))


async def get_all_cookies(web_driver: Browser, with_local_storage=True):
    return await web_driver.cookies.get_all()


async def clear_all_cookies(web_driver: Browser):
    await web_driver.cookies.clear()


async def enable_network_interception(web_driver: Browser):
    await web_driver.connection.send(cdp.fetch.enable())


async def add_request_interception(
    web_driver: Browser, req_fufiller: Callable[[cdp.fetch.RequestPaused], bool]
):
    web_driver.connection.add_handler(cdp.fetch.RequestPaused, req_fufiller)


async def continue_request(
    web_driver: Browser,
    request_id: str,
    url: Optional[str] = None,
    method: Optional[str] = None,
    post_data: Optional[str] = None,
    headers: Optional[List[Dict[str, str]]] = None,
    intercept_response: Optional[bool] = None,
):
    await web_driver.connection.send(
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
    web_driver: Browser,
    request_id: str,
    response_code: int,
    response_headers: Optional[List[Dict[str, str]]] = None,
    binary_response_headers: Optional[str] = None,
    body: Optional[str] = None,
    response_phrase: Optional[str] = None,
):
    await web_driver.connection.send(
        cdp.fetch.fulfill_request(
            request_id=request_id,
            response_code=response_code,
            response_headers=response_headers,
            binary_response_headers=binary_response_headers,
            body=base64.b64encode(body).decode() if body else None,
            response_phrase=response_phrase,
        )
    )


async def set_all_cookies(web_driver: Browser, cookies):
    await web_driver.cookies.set_all(cookies)
