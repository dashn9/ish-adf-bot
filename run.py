#!/usr/bin/python3
import asyncio
import random
import os
import sys
import time
import traceback
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    StaleElementReferenceException,
    UnexpectedAlertPresentException,
)
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
from constants.config import (
    BOT_ID,
    RUN_INFINITELY,
    DEBUG,
    FETCH_BY,
    FETCH_BY_VALUE,
)

boc.FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__))
brc.FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__))


async def restart_plug():
    if not RUN_INFINITELY:
        exit()
    else:
        print("Attempting to rerun operations")
        os.execv(sys.executable, ["python"] + sys.argv)


if FETCH_BY == "scr":
    FETCH_BY_VALUE = [boc.SCREEN_WIDTH, boc.SCREEN_HEIGHT]

identity = Identity()
identity.auto_initiate_identity(FETCH_BY, FETCH_BY_VALUE)

page_info = DataController.fetch_active_random_url()
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


boc.PROXY_WHITELISTED_DOMAINS = page_info.get("proxy_domain_whitelists", "*")


async def run_bot(identity, process_id):
    web_bot = WebBot(
        identity=identity,
        browser_to_use_id=brc.CHROME_ID,
        bot_process_id=process_id,
        no_of_clicks=page_info["page_clicks"],
    )
    web_bot.open_web_browser()
    try:
        web_bot.time_activated = time.time()
        web_bot.web_browser_driver.get(page_info.get("page_url"))

        if random.random() >= identity.ad_keywords_click_probability:
            identity.ad_keywords = None
        ad_click_probability = random.random()
        ad_to_click = None
        if ad_click_probability <= identity.ad_click_probability:
            ad_to_click = identity.ad_type_to_click

        web_bot.set_ad_behaviour_environment(
            ad_to_click=ad_to_click,
            vignette_ad_close_type=page_info["vignette_close_ad_elements_type"],
            vignette_ad_close_name=page_info["vignette_close_ad_elements_name"],
            vignette_ad_open_type=page_info["vignette_open_ad_elements_type"],
            vignette_ad_open_name=page_info["vignette_open_ad_elements_name"],
            in_page_ad_links_type=page_info["in_page_ad_link_elements_type"],
            in_page_ad_links_name=page_info["in_page_ad_link_elements_name"],
            ad_keywords=identity.ad_keywords,
        )
        asyncio.sleep(random.uniform(0, 1))
        if boc.ENGAGE_READER:
            if web_bot.identity.device_type == "is_pc" and random.random() < 0.2:
                web_bot.move_mouse_to_random_area_on_screen()
            if (
                web_bot.read_element_content(
                    web_bot.web_browser_driver.find_element(
                        page_content_element_type, page_content_element_name
                    )
                )
                == "ad_clicked"
            ):
                try:
                    asyncio.sleep(random.uniform(0.7, 1.5))
                    body_element = WebDriverWait(web_bot.web_browser_driver, 4).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    web_bot.read_element_content(body_element)
                    while random.random() < identity.page_depth:
                        web_bot.time_activated = time.time()
                        web_bot.open_link_in_elements([body_element])
                        body_element = WebDriverWait(
                            web_bot.web_browser_driver, 4
                        ).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                        web_bot.read_element_content(body_element)
                except TimeoutException:
                    print(
                        "Body Element Of The Ad Page Could Not Be Found Or Not Loaded On Time"
                    )
            else:
                if page_info.get("related_articles_elements_type") and page_info.get(
                    "related_articles_elements_name"
                ):
                    while random.random() < identity.page_depth:
                        web_bot.time_activated = time.time()
                        web_bot.no_of_clicks = page_info.get("page_clicks")
                        web_bot.open_link_in_elements(
                            web_bot.web_browser_driver.find_elements(
                                related_articles_elements_type,
                                related_articles_elements_name,
                            )
                        )

                        web_bot.read_element_content(
                            web_bot.web_browser_driver.find_element(
                                page_content_element_type, page_content_element_name
                            )
                        )
                        identity.page_depth = identity.page_depth / 2
            if web_bot.identity.device_type == "is_pc":
                web_bot.move_mouse_to_fool_exit_point()
        else:
            # Just a feature for testing, bot doesn't engage if engage-reader was set to false
            asyncio.sleep(
                random.randint(boc.BOT_MIN_ALIVE_TIME, boc.BOT_MAX_ALIVE_TIME)
            )

        try:
            if web_bot.web_browser_driver.session_id:
                print("Updating Cookies To Cloud")
                web_bot.update_cookies_to_cloud()
                web_bot.release_proxies()
                web_bot.proxy_requests_session.close()
                web_bot.cached_requests_session.close()
                web_bot.web_browser_driver.quit()
                DataController.ping_is_alive(BOT_ID)
        except ConnectionRefusedError:
            print(
                "Most likely the Cookie Update job has been done by the daemon responsible for keeping reading "
                "activity on time as a ConnectionRefusedError popped up"
            )

    # These errors occurs when the browser session is terminated and webbot isn't aware
    except (
        NewConnectionError,
        ConnectionRefusedError,
        MaxRetryError,
        ConnectionResetError,
        ProtocolError,
        ReadTimeout,
        StaleElementReferenceException,
        WebDriverException,
        TimeoutException,
        UnexpectedAlertPresentException,
    ):
        if DEBUG:
            print(traceback.format_exc())
            print("The Error Above Was Handled, But Printed For DEBUGing Purpose")
        web_bot.web_browser_driver.quit()
    print("Successfully Completed Activity For Identity:", identity.id)
    restart_plug()


asyncio.run(run_bot(identity, 0))
