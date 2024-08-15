from selenium.common import NoAlertPresentException
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webdriver import WebDriver


def activate_mobile(web_driver: WebDriver, device_metrics: dict, max_touch_points=5):

    if isinstance(web_driver, Chrome):
        # You get and UnexpectedAlertPresentException if you try to activate_mobile on a page that has one present
        try:
            alert = web_driver.switch_to.alert
            alert.accept()
        except NoAlertPresentException:
            pass
        web_driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", device_metrics)
        web_driver.execute_cdp_cmd(
            "Emulation.setTouchEmulationEnabled",
            {"enabled": True, "maxTouchPoints": max_touch_points},
        )
        web_driver.execute_cdp_cmd(
            "Emulation.setEmitTouchEventsForMouse", {"enabled": True}
        )


def activate_all_focus(web_driver: WebDriver):
    if isinstance(web_driver, Chrome):
        web_driver.execute_cdp_cmd(
            "Emulation.setFocusEmulationEnabled", {"enabled": True}
        )


def change_user_agent(
    web_driver: WebDriver,
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
    if isinstance(web_driver, Chrome):
        web_driver.execute_cdp_cmd(
            "Emulation.setUserAgentOverride",
            {
                "userAgent": user_agent,
                "language": language,
                "platform": platform.get("navigator_platform"),
            },
        )
        web_driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": user_agent,
                "language": language,
                "platform": platform.get("navigator_platform"),
            },
        )
        web_driver.execute_cdp_cmd("Emulation.setLocaleOverride", {"locale": "en_GB"})


def set_hardware_concurrency(web_driver: WebDriver, hc=4):
    if isinstance(web_driver, Chrome):
        web_driver.execute_cdp_cmd(
            "Emulation.setHardwareConcurrencyOverride", {"hardwareConcurrency": hc}
        )


def set_timezone(web_driver: WebDriver, timezone="Etc/GMT"):
    if isinstance(web_driver, Chrome):
        web_driver.execute_cdp_cmd(
            "Emulation.setTimezoneOverride", {"timezoneId": timezone}
        )


def get_all_cookies(web_driver: WebDriver):
    if isinstance(web_driver, Chrome):
        return web_driver.execute_cdp_cmd("Storage.getCookies", {})["cookies"]


def clear_all_cookies(web_driver: WebDriver):
    if isinstance(web_driver, Chrome):
        return web_driver.execute_cdp_cmd("Storage.clearCookies", {})


def set_all_cookies(web_driver: WebDriver, cookies):
    if isinstance(web_driver, Chrome):
        print("cookies: ", cookies)
        return web_driver.execute_cdp_cmd("Storage.setCookies", {"cookies": cookies})
