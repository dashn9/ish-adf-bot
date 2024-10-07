#!/usr/bin/python3
import asyncio
import random
import os
import sys
import time
import traceback
import subprocess

from requests import ReadTimeout

from urllib3.exceptions import MaxRetryError, NewConnectionError, ProtocolError

from identity.client import Identity
import constants.browser_constants as brc
import constants.bot_constants as boc
from datacontroller.datacontroller import DataController
from log import logger

from exceptions.identity import TimezoneFetchException
from constants.config import (
    BOT_ID,
    CONTAINERIZED,
    RUN_INFINITELY,
    DEBUG,
    FETCH_BY,
    FETCH_BY_VALUE,
)

# There is an issue where fetching an element position could crash the connection. Fix this by using an event handler to detect if the tab is in a loading stage
# If so, throw an exception, best implement this in nodriver and raise a PR
boc.FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__))
brc.FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__))


async def restart_plug():
    if not RUN_INFINITELY:
        asyncio.get_event_loop().stop()
        exit()
    else:
        print("Attempting to ReRun operations")
        os.execv(sys.executable, ["python", "-u"] + sys.argv)


if FETCH_BY == "scr":
    FETCH_BY_VALUE = [boc.SCREEN_WIDTH, boc.SCREEN_HEIGHT]


async def run_bot(
    identity: Identity,
    page_info: dict,
    process_id,
):
    from bots.webbot import WebBot

    web_bot = WebBot(
        identity=identity,
        browser_to_use_id=brc.CHROME_ID,
        bot_process_id=process_id,
        no_of_clicks=page_info["page_clicks"],
    )
    await web_bot.open_web_browser()
    try:
        web_bot.time_activated = time.time()
        logger.info("{{{ Opening Url On Run... }}}")
        await web_bot.web_browser_driver.get(page_info.get("page_url"))
        await web_bot.wait_for_tab_load()
        logger.info("{{{ Opened Url On Run }}}")
        if random.random() >= identity.ad_keywords_click_probability:
            logger.info(
                f"<--> Negating Ad Click Via Keywords Based On Probability of {identity.ad_keywords_click_probability} <-->"
            )
            identity.ad_keywords = None
        ad_click_probability = random.random()
        ad_to_click = None
        if ad_click_probability <= identity.ad_click_probability:
            logger.info(
                f"<--> Ad: {identity.ad_type_to_click} Set For Engagement <-->"
            )
            ad_to_click = identity.ad_type_to_click

        logger.info("<--> Setting Ad Behaviour Envoronment <-->")
        await web_bot.set_ad_behaviour_environment(
            ad_to_click=ad_to_click,
            vignette_ad_close=page_info["vignette_close_ad_elements"],
            vignette_ad_open=page_info["vignette_open_ad_elements"],
            in_page_ad_links_open=page_info["in_page_open_ad_link_elements"],
            ad_keywords=identity.ad_keywords,
        )
        await asyncio.sleep(random.uniform(0, 1))
        if boc.ENGAGE_READER:
            logger.info("<--> Reader Set To Engage <-->")
            if web_bot.identity.device_type == "computer":
                logger.info("<--> Moving Mouse To Random Area On Document <-->")
                await web_bot.move_mouse_to_random_area_on_document()
                logger.info("<--> Done Moving Mouse To Random Area On Document <--> ")
                logger.info(f"<--> Reading Element: {page_info["page_content_element"]} <--> ")
            if (
                await web_bot.read_element_content(
                    await web_bot.active_tab.select(page_info["page_content_element"])
                )
                == "ad_clicked"
            ):
                # wait this amount to give tab time to fully load, it's excessive, could be lesser in prod, probably switch to config
                await asyncio.sleep(random.uniform(10, 11.5))
                await web_bot.active_tab.sleep(1)
                await web_bot.read_element_content(
                    await web_bot.active_tab.select("body")
                )
                while random.random() < identity.page_depth:
                    web_bot.time_activated = time.time()
                    await web_bot.open_link_in_elements(
                        [await web_bot.active_tab.select("body")]
                    )
                    await web_bot.read_element_content(
                        await web_bot.active_tab.select("body")
                    )
                    identity.page_depth = identity.page_depth / 2
                # print(
                #     "Body Element Of The Ad Page Could Not Be Found Or Not Loaded On Time"
                # )
            else:
                if page_info.get("related_articles_elements", None):
                    while random.random() < identity.page_depth:
                        web_bot.time_activated = time.time()
                        web_bot.no_of_clicks = page_info.get("page_clicks")
                        await web_bot.open_link_in_elements(
                            await web_bot.active_tab.select_all(
                                page_info["related_articles_elements"]
                            )
                        )

                        await web_bot.read_element_content(
                            await web_bot.active_tab.select(
                                page_info["page_content_element"]
                            )
                        )
                        identity.page_depth = identity.page_depth / 2
            if web_bot.identity.device_type == "computer":
                await web_bot.move_mouse_to_fool_exit_point()
        else:
            # Just a feature for testing, bot doesn't engage if engage-reader was set to false
            await asyncio.sleep(
                random.randint(boc.BOT_MIN_ALIVE_TIME, boc.BOT_MAX_ALIVE_TIME)
            )

        try:
            print("Updating Cookies To Cloud")
            await web_bot.update_cookies_to_cloud()
            # await web_bot.release_proxies()
            web_bot.web_browser_driver.stop()
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
    ):
        if DEBUG:
            print(traceback.format_exc())
            print("The Error Above Was Handled, But Printed For DEBUGing Purpose")
        web_bot.web_browser_driver.stop()
    print("Successfully Completed Activity For Identity:", identity.id)


async def main():
    identity = Identity()
    try:
        await identity.auto_initiate_identity(FETCH_BY, FETCH_BY_VALUE)
    except TimezoneFetchException:
        if FETCH_BY == "random":
            for _ in range(12):
                try:
                    print(
                        f"Initiating Identity with ID: {identity.id} failed, Reinitiating at: {_}"
                    )
                    await identity.auto_initiate_identity(FETCH_BY, FETCH_BY_VALUE)
                    break
                except TimezoneFetchException:
                    await asyncio.sleep(0.5)
    if CONTAINERIZED:
        screen_width = identity.screen_width
        screen_height = identity.screen_height
        if identity.device_type == "smartphone":
            # Seperate this below into config
            boc.SCREEN_WIDTH = screen_width = 700
            boc.SCREEN_HEIGHT = screen_height = 1100
        subprocess.run(
            [
                brc.FULL_DIRECTORY_PATH + "/create_display.sh",
                f"{screen_width}x{screen_height}x24",
            ]
        )
    page_info = await DataController.fetch_active_random_url()

    # please correct config, and use the one in it
    boc.PROXY_WHITELISTED_DOMAINS = page_info.get("proxy_domain_whitelists", "*")
    boc.PROXY_WHITELISTED_VIP_DOMAINS = page_info.get("proxy_domain_vip_whitelists", [])

    await run_bot(identity, page_info, 0)
    await restart_plug()


asyncio.run(main())
