import base64

from typing import Callable, Optional, List, Dict
from nodriver import Browser, cdp


async def activate_mobile(
    web_driver: Browser, device_metrics: dict, max_touch_points=5
):
    alert = web_driver.switch_to.alert
    alert.accept()
    web_driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", device_metrics)
    web_driver.execute_cdp_cmd(
        "Emulation.setTouchEmulationEnabled",
        {"enabled": True, "maxTouchPoints": max_touch_points},
    )
    web_driver.execute_cdp_cmd(
        "Emulation.setEmitTouchEventsForMouse", {"enabled": True}
    )


async def activate_all_focus(web_driver: Browser):
    web_driver.execute_cdp_cmd("Emulation.setFocusEmulationEnabled", {"enabled": True})


async def change_user_agent(
    web_driver: Browser,
    user_agent,
    platform={
        "architecture": None,
        "bitness": None,
        "navigator_platform": "",
        "name": None,
        "version": None,
    },
    language=["en-US", "en"],
):
    await web_driver.main_tab.send(
        cdp.emulation.set_user_agent_override(
            user_agent=user_agent,
            accept_language=",".join(language),
            platform=platform["navigator_platform"],
            # user_agent_metadata=None,
        )
    )
    await web_driver.main_tab.send(cdp.emulation.set_locale_override(language[0]))


async def set_hardware_concurrency(web_driver: Browser, hc=4):
    await web_driver.main_tab.send(cdp.emulation.set_hardware_concurrency_override(hc))


async def set_timezone(web_driver: Browser, timezone="Etc/GMT"):
    await web_driver.main_tab.send(cdp.emulation.set_timezone_override(timezone))


async def get_all_cookies(web_driver: Browser):
    await web_driver.execute_cdp_cmd("Storage.getCookies", {})["cookies"]


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
    print("cookies: ", cookies)
    await web_driver.cookies.set_all(cookies)
