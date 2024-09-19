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
        await web_bot.web_browser_driver.get(page_info.get("page_url"))

        if random.random() >= identity.ad_keywords_click_probability:
            identity.ad_keywords = None
        ad_click_probability = random.random()
        ad_to_click = None
        if ad_click_probability <= identity.ad_click_probability:
            ad_to_click = identity.ad_type_to_click

        await web_bot.set_ad_behaviour_environment(
            ad_to_click=ad_to_click,
            vignette_ad_close=page_info["vignette_close_ad_elements"],
            vignette_ad_open=page_info["vignette_open_ad_elements"],
            in_page_ad_links_open=page_info["in_page_open_ad_link_elements"],
            ad_keywords=identity.ad_keywords,
        )
        await asyncio.sleep(random.uniform(0, 1))
        if boc.ENGAGE_READER:
            if web_bot.identity.device_type == "computer":
                await web_bot.move_mouse_to_random_area_on_document()
            if (
                await web_bot.read_element_content(
                    await web_bot.active_tab.select(page_info["page_content_element"])
                )
                == "ad_clicked"
            ):
                # Reload is still triggered by the new tab detector handler, thisone to make sure
                await asyncio.sleep(2.5)
                await web_bot.active_tab.reload()
                # wait this amount to give tab time to fully load
                await asyncio.sleep(random.uniform(10, 12.5))
                await web_bot.read_element_content(
                    await web_bot.active_tab.select("body", 15)
                )
                while random.random() < identity.page_depth:
                    web_bot.time_activated = time.time()
                    body_element = await web_bot.active_tab.select("body")
                    await web_bot.open_link_in_elements([body_element])
                    await web_bot.read_element_content(body_element)
                # print(
                #     "Body Element Of The Ad Page Could Not Be Found Or Not Loaded On Time"
                # )
            else:
                if page_info.get("related_articles_elements_type") and page_info.get(
                    "related_articles_elements_name"
                ):
                    while random.random() < identity.page_depth:
                        web_bot.time_activated = time.time()
                        web_bot.no_of_clicks = page_info.get("page_clicks")
                        web_bot.open_link_in_elements(
                            web_bot.active_tab.select_all(
                                page_info["related_articles_elements"]
                            )
                        )

                        web_bot.read_element_content(
                            web_bot.active_tab.select(page_info["page_content_element"])
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
            await web_bot.release_proxies()
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

    await identity.auto_initiate_identity(FETCH_BY, FETCH_BY_VALUE)

    subprocess.run(
        [
            brc.FULL_DIRECTORY_PATH + "/create_display.sh",
            f"{identity.screen_width}x{identity.screen_height}x24",
        ]
    )
    page_info = await DataController.fetch_active_random_url()

    boc.PROXY_WHITELISTED_DOMAINS = page_info.get("proxy_domain_whitelists", "*")

    await run_bot(identity, page_info, 0)
    await restart_plug()


asyncio.run(main())
