import os

# With Great Power Comes Great Responsibility

# Time Constants
IMPLICITLY_WAIT_TIME = 15

# FULL WORKING DIRECTORY
FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__)).replace(
    "/constants", ""
)

# Selenium Web Drivers Locations
CHROME_WEBDRIVER_LOCATION = "/executables/drivers/chrome/chromedriver"
FIREFOX_WEBDRIVER_LOCATION = "/executables/drivers/firefox/firefoxdriver"

BOT_MAX_ALIVE_TIME = 90
BOT_MIN_ALIVE_TIME = 35

MAX_OVPN_CONNECT_RETRIES = 1
OVPN_MAX_WAIT_TIME_TILL_IP_IMPROVISE = 7

PX_VALUE_TO_CHECK_WHEN_SCROLL_TO_POINT = 250

NORDVPN_OVPN_FILE_PATH = os.getenv("NORDVPN_OVPN_FILE_PATH")

IPVANISH_OVPN_FILE_PATH = os.getenv("IPVANISH_OVPN_FILE_PATH")

SCREEN_WIDTH = os.getenv("SCREEN_WIDTH")

SCREEN_HEIGHT = os.getenv("SCREEN_HEIGHT")

UP_TASKBAR_HEIGHT = 5

# Proxies
USE_PROXY = False
PROXY_PRODUCT = "smartproxy.com"
PROXY_GEO_TARGET_AREA = "city"
PROXY_SESSION_DURATION = 2

PROXY_USERNAME = "adfrpr"
PROXY_PASSWORD = "y4nSMS602jww"
PROXY_PORT = 10000
PROXY_STICKY_TEMPLATE = "user-<user>-country-<geo_target>-sessionduration-<ss_duration>:<pass>@<geo_target_area>.smartproxy.com:<port>"
PROXY_RANDOM_TEMPLATE = "user-<user>:<pass>@gate.smartproxy.com:10000"

PROXY_BLACKLISTED_EXTENSIONS = [
    ".css",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".woff",
    ".woff2",
    ".ttf",
    ".ico",
    ".webm",
    ".ogg",
    ".wav",
    ".mp3",
    ".mp4",
]

PROXY_WHITELISTED_DOMAINS = [
    "whouseem.com",
    "dudialgator.com",
    "bedrapiona.com",
    "fleraprt.com",
]
PROXY_BLACKLISTED_DOMAINS = []
ALLOW_URL_THROUGH_PROXY_IF_MATCHES_BROWSER_ACTIVE_URL = True

USE_MOUSE_READ_PROBABILITY = 0.62

IDENTITY_BASE_HOST = "https://127.0.0.1:5000/api/"
