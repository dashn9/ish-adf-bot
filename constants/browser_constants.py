import os

# With Great Power Comes Great Responsibility

# FULL WORKING DIRECTORY
FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__)).replace(
    "/constants", ""
)
CHROME_DATA_DIRECTORY = FULL_DIRECTORY_PATH + "/data/browsers/chrome"

IGNORE_SSL = False

# Identify Browser To Use
RAND_BROWSER = 9999
NO_BROWSER = 0

CHROME_ID = 1
FIREFOX_ID = 2

# Browser Binaries/Executables Locations
CHROME_BINARY_LOCATION = r"/bin/google-chrome-stable"
FIREFOX_BINARY_LOCATION = r"/opt/firefox/firefox"

MAXIMUM_WINDOW_PROBABILITY = 0.92
KIOSK_MODE_PROBABILITY = 0.6

CHROMIUM_SPECIFIC_HEADERS = {
    "device-memory",
    "downlink",
    "dpr",
    "ect",
    "rtt",
    "viewport-width",
    "sec-ch-device-memory",
    "sec-ch-dpr",
    "sec-ch-prefers-color-scheme",
    "sec-ch-prefers-reduced-motion",
    "sec-ch-prefers-reduced-transparency",
    "sec-ch-ua",
    "sec-ch-ua-arch",
    "sec-ch-ua-bitness",
    "sec-ch-ua-full-version",
    "sec-ch-ua-full-version-list",
    "sec-ch-ua-mobile",
    "sec-ch-ua-model",
    "sec-ch-ua-platform",
    "sec-ch-ua-platform-version",
    "sec-ch-ua-wow64",
    "sec-ch-viewport-height",
    "sec-ch-viewport-width",
    "architecture",
    "bitness",
    "brands",
    "fullversionlist",
    "mobile",
    "model",
    "platform",
    "platformversion",
    "uafullversion",
    "wow64",
}
