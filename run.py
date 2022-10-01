import getopt
import os
import random
import sys
import time
import multiprocessing
import json

from selenium.webdriver.common.by import By

from bots.webbot import WebBot
from identity.client import Identity
import constants.browser_constants as brc
import constants.bot_constants as boc
from datacontroller.datacontroller import DataController

boc.FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__))
brc.FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__))
try:
    opts, args = getopt.getopt(sys.argv[1:], None, longopts=["nordvpn-ovpn-files-path=", "ipvanish-ovpn-files-path=",
                                                  "screen-width=", "screen-height="])

    for opt, arg in opts:
        if opt in "--nordvpn-ovpn-files-path":
            boc.NORDVPN_OVPN_FILE_PATH = arg
        elif opt in "--ipvanish-ovpn-files-path":
            boc.IPVANISH_OVPN_FILE_PATH = arg
        elif opt in "--screen-width":
            boc.SCREEN_WIDTH = int(arg)
        elif opt in "--screen-height":
            boc.SCREEN_HEIGHT = int(arg)

except getopt.GetoptError as error:
    print(error)
    exit()

if not boc.NORDVPN_OVPN_FILE_PATH:
    print("It Is Extremely Advisable That A Path Value For The --nordvpn-ovpn-files-path Is Set, Even Better Is To"
          " Set An ENV Variable NORDVPN_OVPN_FILE_PATH")
if not boc.IPVANISH_OVPN_FILE_PATH:
    print("It Is Extremely Advisable That A Path Value For The --ipvanish-ovpn-files-path Is Set, Even Better Is To"
          " Set An ENV Variable IPVANISH_OVPN_FILE_PATH")
if not boc.SCREEN_WIDTH:
    print("The Screen Width Flag --screen-width Must Be Set, Even Better Is To"
          " Set An ENV Variable SCREEN_WIDTH")
    exit()
if not boc.SCREEN_HEIGHT:
    print("The Screen Height Flag --screen-height Must Be Set, Even Better Is To"
          " Set An ENV Variable SCREEN_HEIGHT")
    exit()
while True:

    identity = Identity()
    identity.auto_initiate_identity("scr", [boc.SCREEN_WIDTH, boc.SCREEN_HEIGHT])
    try:
        active_bot_processes = []
        page_info = json.loads(DataController.fetch_active_random_url())
        page_content_element_type = By.ID
        page_content_element_name = page_info.get("page_content_element_name")
        related_articles_elements_type = By.CLASS_NAME
        related_articles_elements_name = page_info.get("related_articles_elements_name")
        if page_info.get("page_content_element_type") == "class":
            page_content_element_type = By.CLASS_NAME
        if page_info.get("related_articles_elements_type") == "id":
            related_articles_elements_type = By.ID
        def run_bot(identity, process_id):
            try:
                web_bot = WebBot(identity=identity, browser_to_use_id=brc.CHROME_ID,
                            driver_path=boc.FULL_DIRECTORY_PATH+boc.WEB_DRIVERS_BASE_LOCATION+boc.WEB_DRIVERS_CHROME_LOCATION+
                                        boc.CHROME_WEBDRIVER, bot_process_id=process_id)
                web_bot.open_web_browser()
                web_bot.time_activated = time.time()
                web_bot.web_browser_driver.get(page_info.get("page_url"))
                time.sleep(random.uniform(0, 2))
                if web_bot.identity.device_type == "is_pc" and random.random() < 0.6:
                    web_bot.move_mouse_to_random_area_on_screen()
                web_bot.read_element_content(web_bot.web_browser_driver.find_element(page_content_element_type,
                                                                                     page_content_element_name))
                if page_info.get("related_articles_elements_type") and page_info.get("related_articles_elements_name"):
                    while random.random() < identity.page_depth:
                        web_bot.time_activated = time.time()
                        web_bot.open_link_in_related_articles_section(web_bot.web_browser_driver.find_elements(
                            related_articles_elements_type, related_articles_elements_name))

                        web_bot.read_element_content(web_bot.web_browser_driver.find_element(page_content_element_type,
                                                                                             page_content_element_name))
                        identity.page_depth = identity.page_depth / 2
                if web_bot.identity.device_type == "is_pc":
                    web_bot.move_mouse_to_fool_exit_point()

                print("Updating Cookies To Cloud")
                web_bot.update_cookies_to_cloud()
                if hasattr(web_bot, "web_browser_driver"):
                    web_bot.web_browser_driver.quit()
                    del web_bot.web_browser_driver
                del web_bot
            except Exception as err:
                print(err)
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
        identity.disconnect_all_vpn()
        print("Successfully Completed Activity For Identity:", identity.id)
    except Exception as err:
        print("Something Went Wrong, Most Probably Server Refuses To Provide Identity, "
              "Sleeping For 1:30 Minutes Then Retrying")
        print(f"Extra Error Info: {err}")
        time.sleep(90)