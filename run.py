#!/usr/bin/python3
import random
import os
import sys
import time
import multiprocessing
import json
import configparser
import traceback
from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from requests import ReadTimeout

from selenium.webdriver.common.by import By
from urllib3.exceptions import MaxRetryError, NewConnectionError, ProtocolError

from bots.webbot import WebBot
from identity.client import Identity
import constants.browser_constants as brc
import constants.bot_constants as boc
from datacontroller.datacontroller import DataController

boc.FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__))
brc.FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(boc.FULL_DIRECTORY_PATH + "/config.ini")

run_infinitely = False
debug = True
if "OPTIONS" in config:
    options = config["OPTIONS"]
    boc.NORDVPN_OVPN_FILE_PATH = options.get("nordvpn-ovpn-files-path", boc.NORDVPN_OVPN_FILE_PATH)
    boc.IPVANISH_OVPN_FILE_PATH = options.get("ipvanish-ovpn-files-path", boc.IPVANISH_OVPN_FILE_PATH)
    boc.SCREEN_WIDTH = options.getint("screen-width", boc.SCREEN_WIDTH)
    boc.SCREEN_HEIGHT = options.getint("screen-height", boc.SCREEN_HEIGHT)
    boc.UP_TASKBAR_HEIGHT = options.getint("up-taskbar-height", boc.UP_TASKBAR_HEIGHT)
    debug = options.getboolean("debug", True)

if "WAIT_CONDITIONS" in config:
    options = config["OPTIONS"]

    boc.IMPLICITLY_WAIT_TIME = options.get("implicitly-wait-time", boc.IMPLICITLY_WAIT_TIME)

if "PROXY" in config:
    proxy_config = config["PROXY"]
    boc.PROXY_PRODUCT = proxy_config.get("proxy-product", boc.PROXY_PRODUCT)
    boc.PROXY_GEO_TARGET_AREA = proxy_config.get("proxy-geo-target-area", boc.PROXY_GEO_TARGET_AREA)
    boc.PROXY_SESSION_DURATION = proxy_config.getint("proxy-session-duration", boc.PROXY_SESSION_DURATION)
    boc.PROXY_USERNAME = proxy_config.get("proxy-username", boc.PROXY_USERNAME)
    boc.PROXY_PASSWORD = proxy_config.get("proxy-password", boc.PROXY_PASSWORD)
    boc.PROXY_PORT = proxy_config.getint("proxy-port", boc.PROXY_PORT)
    boc.PROXY_STICKY_TEMPLATE = proxy_config.get("proxy-sticky-template", boc.PROXY_STICKY_TEMPLATE)
    boc.PROXY_RANDOM_TEMPLATE = proxy_config.get("proxy-random-template", boc.PROXY_RANDOM_TEMPLATE)

if "BOT" in config:
    bot_conf = config["BOT"]

    boc.BOT_MAX_ALIVE_TIME = bot_conf.getint("max-alive-time", boc.BOT_MAX_ALIVE_TIME)
    boc.BOT_MIN_ALIVE_TIME = bot_conf.getint("min-alive-time", boc.BOT_MIN_ALIVE_TIME)
    run_infinitely = bot_conf.getboolean("run-infinitely", False)

if "OVPN" in config:
    ovpn = config["OVPN"]

    boc.MAX_OVPN_CONNECT_RETRIES = ovpn.getint("max-connect-retries", boc.MAX_OVPN_CONNECT_RETRIES)
    boc.OVPN_MAX_WAIT_TIME_TILL_IP_IMPROVISE = ovpn.getint("max-wait-time", boc.OVPN_MAX_WAIT_TIME_TILL_IP_IMPROVISE)

if "SCROLL" in config:
    scroll = config["SCROLL"]

    boc.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT = scroll.getint("px-value", boc.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT)

if "WEB_DRIVERS" in config:
    web_drivers = config["WEB_DRIVERS"]

    boc.WEB_DRIVERS_BASE_LOCATION = web_drivers.get("base-location", boc.WEB_DRIVERS_BASE_LOCATION)
    boc.WEB_DRIVERS_CHROME_LOCATION = web_drivers.get("chrome-location", boc.WEB_DRIVERS_CHROME_LOCATION)
    boc.CHROME_WEBDRIVER = web_drivers.get("chrome-webdriver", boc.CHROME_WEBDRIVER)
    boc.WEB_DRIVERS_GECKO_LOCATION = web_drivers.get("gecko-location", boc.WEB_DRIVERS_GECKO_LOCATION)
    boc.GECKO_WEBDRIVER = web_drivers.get("gecko-webdriver", boc.GECKO_WEBDRIVER)
    boc.WEB_DRIVERS_FIREFOX_LOCATION = web_drivers.get("firefox-location", boc.WEB_DRIVERS_FIREFOX_LOCATION)
    boc.FIREFOX_WEBDRIVER = web_drivers.get("firefox-webdriver", boc.FIREFOX_WEBDRIVER)

if "BROWSER" in config:
    browser = config["BROWSER"]

    brc.CHROME_BINARY_LOCATION = browser.get("chrome-binary-location", brc.CHROME_BINARY_LOCATION)
    brc.FIREFOX_BINARY_LOCATION = browser.get("firefox-binary-location", brc.FIREFOX_BINARY_LOCATION)

if "SITE" in config:
    ads = config["SITE"]

    brc.SITE_DOMAIN = ads.get("site-domain", brc.SITE_DOMAIN)
    brc.AD_PROVIDERS = ads.get("ad-providers", brc.AD_PROVIDERS).split(",")
    brc.AD_ATTR = ads.get("attr", brc.AD_ATTR)
    brc.AD_ATTR_NAME = ads.get("attr-name", brc.AD_ATTR_NAME)
    brc.AD_CLOSE_ATTR = ads.get("close-attr", brc.AD_CLOSE_ATTR)
    brc.AD_CLOSE_ATTR_NAME = ads.get("close-attr-name", brc.AD_CLOSE_ATTR_NAME)

if "IDENTITY" in config:
    idy = config["IDENTITY"]
    fetch_by = idy.get("fetch-by", "scr")
    fetch_by_value = idy.get("fetch-by-value", [boc.SCREEN_WIDTH, boc.SCREEN_HEIGHT])

if fetch_by == "device_type":
    fetch_by_value = fetch_by_value

elif fetch_by == "proxy_geo":
    fetch_by_value = fetch_by_value

elif fetch_by == "id":
    fetch_by_value = int(fetch_by_value)

else:
    fetch_by = "scr"
    fetch_by_value = [boc.SCREEN_WIDTH, boc.SCREEN_HEIGHT]

identity = Identity()
identity.auto_initiate_identity(fetch_by, fetch_by_value)
active_bot_processes = []
page_info = json.loads(DataController.fetch_active_random_url())
page_content_element_type = By.ID
page_content_element_name = page_info.get("page_content_element_name")
related_articles_elements_type = By.CLASS_NAME
related_articles_elements_name = page_info.get("related_articles_elements_name")
if page_info.get("page_content_element_type") == "class":
    page_content_element_type = By.CLASS_NAME
elif page_info.get("page_content_element_type") == "tag_name":
    page_content_element_type = By.TAG_NAME

if page_info.get("related_articles_elements_type") == "id":
    related_articles_elements_type = By.ID
elif page_info.get("related_articles_elements_type") == "tag_name":
    related_articles_elements_type = By.TAG_NAME


def run_bot(identity, process_id):
    web_bot = WebBot(identity=identity, browser_to_use_id=brc.CHROME_ID,
                     driver_path=boc.FULL_DIRECTORY_PATH + boc.WEB_DRIVERS_BASE_LOCATION + boc.WEB_DRIVERS_CHROME_LOCATION +
                                 boc.CHROME_WEBDRIVER, bot_process_id=process_id, no_of_clicks=page_info["page_clicks"])
    web_bot.open_web_browser(use_proxy=True)
    try:
        web_bot.time_activated = time.time()
        web_bot.web_browser_driver.get(page_info.get("page_url"))
        if random.random() <= identity.ad_click_probability:
            if random.random() >= identity.ad_keywords_click_probability:
                identity.ad_keywords = None
            web_bot.set_ad_behaviour_environment(ad_links_type=page_info["ad_link_elements_type"],
                                                 ad_links_name=page_info["ad_link_elements_name"],
                                                 maximum_no_of_ads=page_info["maximum_no_of_ads"],
                                                 ad_keywords=identity.ad_keywords)
        time.sleep(random.uniform(0, 1))
        if web_bot.identity.device_type == "is_pc" and random.random() < 0.2:
            web_bot.move_mouse_to_random_area_on_screen()
        if web_bot.read_element_content(web_bot.web_browser_driver.find_element(page_content_element_type,
                                                                             page_content_element_name)) == \
            "ad_clicked":
            web_bot.time_activated = time.time()
            try:
                time.sleep(random.uniform(0.7, 1.5))
                body_element = WebDriverWait(web_bot.web_browser_driver, 4).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                web_bot.read_element_content(body_element)
                while random.random() < identity.page_depth:
                    web_bot.time_activated = time.time()
                    web_bot.open_link_in_related_articles_section([body_element])
                    body_element = WebDriverWait(web_bot.web_browser_driver, 4).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    web_bot.read_element_content(body_element)
            except TimeoutException:
                print("Body Element Of The Ad Page Could Not Be Found Or Not Loaded On Time")
        else:
            if page_info.get("related_articles_elements_type") and page_info.get("related_articles_elements_name"):
                while random.random() < identity.page_depth:
                    web_bot.time_activated = time.time()
                    web_bot.no_of_clicks = page_info.get("page_clicks")
                    web_bot.open_link_in_related_articles_section(web_bot.web_browser_driver.find_elements(
                        related_articles_elements_type, related_articles_elements_name))

                    web_bot.read_element_content(web_bot.web_browser_driver.find_element(page_content_element_type,
                                                                                         page_content_element_name))
                    identity.page_depth = identity.page_depth / 2
        if web_bot.identity.device_type == "is_pc":
            web_bot.move_mouse_to_fool_exit_point()

        try:
            web_bot.requests_session.close()
            web_bot.cached_requests_session.close()
            if web_bot.web_browser_driver.session_id:
                print("Updating Cookies To Cloud")
                web_bot.update_cookies_to_cloud()
                web_bot.web_browser_driver.quit()
        except ConnectionRefusedError:
            print("Most likely the Cookie Update job has been done by the daemon responsible for keeping reading "
                  "activity on time as a ConnectionRefusedError popped up")

    # These errors occurs when the browser session is terminated and webbot isn't aware
    except (NewConnectionError, ConnectionRefusedError, MaxRetryError, ConnectionResetError, ProtocolError, ReadTimeout,
            StaleElementReferenceException):
        if debug:
            print(traceback.format_exc())
            print("The Error Above Was Handled, But Printed For Debugging Purpose")
        web_bot.web_browser_driver.quit()

no_of_bots = 1
if no_of_bots == 1:
    run_bot(identity, 0)
else:
    for i in range(no_of_bots):
        print(f"Identity Successfully Initiated, Attaching Identity(ID = {identity.id}) To Bot process {i}")
        bot_process = multiprocessing.Process(target=run_bot, args=(identity, i,), name=f"bot_process_{i}")
        active_bot_processes.append(bot_process)
        bot_process.start()

    for bot_process in active_bot_processes:
        bot_process.join()

active_bot_processes = []
WebBot.active_on_mouse_movement.value = -498
print("Successfully Completed Activity For Identity:", identity.id)
if not run_infinitely:
    exit()
else:
    print("Attempting to rerun operations")
    os.execv(sys.executable, ['python3.10'] + sys.argv)

