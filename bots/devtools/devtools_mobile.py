from selenium.webdriver import Chrome, Firefox, Edge
from selenium.webdriver.remote.webdriver import WebDriver


def activate_mobile(web_driver: WebDriver, device_metrics: dict, max_touch_points=5):
    if isinstance(web_driver, Chrome):
        web_driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", device_metrics)
        web_driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled",
                                   {'enabled': True, 'maxTouchPoints': max_touch_points})
        web_driver.execute_cdp_cmd("Emulation.setEmitTouchEventsForMouse",
                                   {'enabled': True})

