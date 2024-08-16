import configparser

import constants.browser_constants as brc
import constants.bot_constants as boc
from constants import config

configParser = configparser.ConfigParser()
configParser.read(boc.FULL_DIRECTORY_PATH + "/config.ini")


def load_configurations():
    if "OPTIONS" in configParser:
        options = configParser["OPTIONS"]
        boc.NORDVPN_OVPN_FILE_PATH = options.get(
            "nordvpn-ovpn-files-path", boc.NORDVPN_OVPN_FILE_PATH
        )
        boc.IPVANISH_OVPN_FILE_PATH = options.get(
            "ipvanish-ovpn-files-path", boc.IPVANISH_OVPN_FILE_PATH
        )
        boc.SCREEN_WIDTH = options.getint("screen-width", boc.SCREEN_WIDTH)
        boc.SCREEN_HEIGHT = options.getint("screen-height", boc.SCREEN_HEIGHT)
        boc.UP_TASKBAR_HEIGHT = options.getint(
            "up-taskbar-height", boc.UP_TASKBAR_HEIGHT
        )
        config.DEBUG = options.getboolean("debug", True)
        config.CONTAINERIZED = options.getboolean("containerized", False)

    if "WAIT_CONDITIONS" in configParser:
        options = configParser["OPTIONS"]

        boc.IMPLICITLY_WAIT_TIME = options.get(
            "implicitly-wait-time", boc.IMPLICITLY_WAIT_TIME
        )

    if "PROXY" in configParser:
        proxy_config = configParser["PROXY"]
        boc.USE_PROXY = proxy_config.getboolean("use-proxy", True)

    if "BOT" in configParser:
        bot_conf = configParser["BOT"]

        boc.BOT_MAX_ALIVE_TIME = bot_conf.getint(
            "max-alive-time", boc.BOT_MAX_ALIVE_TIME
        )
        boc.BOT_MIN_ALIVE_TIME = bot_conf.getint(
            "min-alive-time", boc.BOT_MIN_ALIVE_TIME
        )
        boc.USE_MOUSE_READ_PROBABILITY = bot_conf.getfloat(
            "mouse-use-probability", boc.USE_MOUSE_READ_PROBABILITY
        )
        boc.ENGAGE_READER = bot_conf.getboolean("engage-reader", boc.ENGAGE_READER)
        config.BOT_ID = bot_conf.get("bot-id", None)
        config.RUN_INFINITELY = bot_conf.getboolean("run-infinitely", False)

    if "BROWSER" in configParser:
        browser_conf = configParser["BROWSER"]

        brc.MAXIMUM_WINDOW_PROBABILITY = browser_conf.getfloat(
            "maximum-window-probability", brc.MAXIMUM_WINDOW_PROBABILITY
        )
        brc.KIOSK_MODE_PROBABILITY = browser_conf.getfloat(
            "kiosk-mode-probability", brc.KIOSK_MODE_PROBABILITY
        )
        brc.IGNORE_SSL = browser_conf.getboolean("ignore-ssl", brc.IGNORE_SSL)

    if "OVPN" in configParser:
        ovpn = configParser["OVPN"]

        boc.MAX_OVPN_CONNECT_RETRIES = ovpn.getint(
            "max-connect-retries", boc.MAX_OVPN_CONNECT_RETRIES
        )
        boc.OVPN_MAX_WAIT_TIME_TILL_IP_IMPROVISE = ovpn.getint(
            "max-wait-time", boc.OVPN_MAX_WAIT_TIME_TILL_IP_IMPROVISE
        )

    if "SCROLL" in configParser:
        scroll = configParser["SCROLL"]

        boc.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT = scroll.getint(
            "px-value", boc.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT
        )

    if "EXECUTABLES" in configParser:
        executables = configParser["EXECUTABLES"]

        boc.CHROME_WEBDRIVER_LOCATION = executables.get(
            "chrome-webdriver-location", boc.CHROME_WEBDRIVER_LOCATION
        )
        boc.FIREFOX_WEBDRIVER_LOCATION = executables.get(
            "firefox-webdriver-location", boc.FIREFOX_WEBDRIVER_LOCATION
        )

        brc.CHROME_BINARY_LOCATION = executables.get(
            "chrome-binary-location", brc.CHROME_BINARY_LOCATION
        )
        brc.FIREFOX_BINARY_LOCATION = executables.get(
            "firefox-binary-location", brc.FIREFOX_BINARY_LOCATION
        )

    if "SITE" in configParser:
        ads = configParser["SITE"]

        boc.PROXY_WHITELISTED_DOMAINS = ads.get(
            "proxy-whitelisted-domains", boc.PROXY_WHITELISTED_DOMAINS
        ).split(",")
        boc.PROXY_blackLISTED_DOMAINS = ads.get(
            "proxy-blacklisted-domains", boc.PROXY_BLACKLISTED_DOMAINS
        ).split(",")
        boc.PROXY_BLACKLISTED_EXTENSIONS = ads.get(
            "proxy-blacklisted-extensions", boc.PROXY_BLACKLISTED_EXTENSIONS
        ).split(",")
        boc.ALLOW_URL_THROUGH_PROXY_IF_MATCHES_BROWSER_ACTIVE_URL = ads.getboolean(
            "allow-url-through-proxy-if-matches-browser-active-url",
            boc.ALLOW_URL_THROUGH_PROXY_IF_MATCHES_BROWSER_ACTIVE_URL,
        )

    if "IDENTITY" in configParser:
        idy = configParser["IDENTITY"]
        config.FETCH_BY = idy.get("fetch-by", "scr")
        config.FETCH_BY_VALUE = idy.get(
            "fetch-by-value", [boc.SCREEN_WIDTH, boc.SCREEN_HEIGHT]
        )

    if "IDENTITY_ENDPOINTS" in configParser:
        idy_edp = configParser["IDENTITY_ENDPOINTS"]
        boc.IDENTITY_API_BASE_HOST = idy_edp.get(
            "base-host", "http://localhost:5000/api/"
        )

    if "DEBUGGING" in configParser:
        dbg = configParser["DEBUGGING"]
        config.PRINT_NETWORK = dbg.getboolean("print-network", config.PRINT_NETWORK)


load_configurations()
