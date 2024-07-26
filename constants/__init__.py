import configparser

import constants.browser_constants as brc
import constants.bot_constants as boc
import constants.config as cfg_mod

config = configparser.ConfigParser()
config.read(boc.FULL_DIRECTORY_PATH + "/config.ini")


def load_configurations():
    if "OPTIONS" in config:
        options = config["OPTIONS"]
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
        cfg_mod.DEBUG = options.getboolean("debug", True)
        cfg_mod.CONTAINERIZED = options.getboolean("containerized", False)

    if "WAIT_CONDITIONS" in config:
        options = config["OPTIONS"]

        boc.IMPLICITLY_WAIT_TIME = options.get(
            "implicitly-wait-time", boc.IMPLICITLY_WAIT_TIME
        )

    if "PROXY" in config:
        proxy_config = config["PROXY"]
        boc.USE_PROXY = proxy_config.getboolean("use-proxy", True)

    if "BOT" in config:
        bot_conf = config["BOT"]

        boc.BOT_MAX_ALIVE_TIME = bot_conf.getint(
            "max-alive-time", boc.BOT_MAX_ALIVE_TIME
        )
        boc.BOT_MIN_ALIVE_TIME = bot_conf.getint(
            "min-alive-time", boc.BOT_MIN_ALIVE_TIME
        )
        boc.USE_MOUSE_READ_PROBABILITY = bot_conf.getfloat(
            "mouse-use-probability", boc.USE_MOUSE_READ_PROBABILITY
        )
        cfg_mod.BOT_ID = bot_conf.get("bot-id", None)
        cfg_mod.RUN_INFINITELY = bot_conf.getboolean("run-infinitely", False)

    if "BROWSER" in config:
        browser_conf = config["BROWSER"]

        brc.MAXIMUM_WINDOW_PROBABILITY = browser_conf.getfloat(
            "maximum-window-probability", brc.MAXIMUM_WINDOW_PROBABILITY
        )
        brc.KIOSK_MODE_PROBABILITY = browser_conf.getfloat(
            "kiosk-mode-probability", brc.KIOSK_MODE_PROBABILITY
        )
        brc.IGNORE_SSL = browser_conf.getboolean("ignore-ssl", brc.IGNORE_SSL)

    if "OVPN" in config:
        ovpn = config["OVPN"]

        boc.MAX_OVPN_CONNECT_RETRIES = ovpn.getint(
            "max-connect-retries", boc.MAX_OVPN_CONNECT_RETRIES
        )
        boc.OVPN_MAX_WAIT_TIME_TILL_IP_IMPROVISE = ovpn.getint(
            "max-wait-time", boc.OVPN_MAX_WAIT_TIME_TILL_IP_IMPROVISE
        )

    if "SCROLL" in config:
        scroll = config["SCROLL"]

        boc.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT = scroll.getint(
            "px-value", boc.PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT
        )

    if "EXECUTABLES" in config:
        executables = config["EXECUTABLES"]

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

    if "SITE" in config:
        ads = config["SITE"]

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

    if "IDENTITY" in config:
        idy = config["IDENTITY"]
        cfg_mod.FETCH_BY = idy.get("fetch-by", "scr")
        cfg_mod.FETCH_BY_VALUE = idy.get(
            "fetch-by-value", [boc.SCREEN_WIDTH, boc.SCREEN_HEIGHT]
        )
    if "IDENTITY_ENDPOINTS" in config:
        idy_edp = config["IDENTITY_ENDPOINTS"]
        boc.IDENTITY_API_BASE_HOST = idy_edp.get(
            "base-host", "http://localhost:5000/api/"
        )


load_configurations()
