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


async def set_all_cookies(web_driver: Browser, cookies):
    print("cookies: ", cookies)
    await web_driver.cookies.set_all(cookies)
