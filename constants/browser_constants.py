import os

# With Great Power Comes Great Responsibility

# FULL WORKING DIRECTORY
FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__)).replace(
    "/constants", ""
)

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
