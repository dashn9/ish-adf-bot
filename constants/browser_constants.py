import os
# With Great Power Comes Great Responsibility

# FULL WORKING DIRECTORY
FULL_DIRECTORY_PATH = os.path.dirname(os.path.realpath(__file__)).replace("/constants", "")

# Identify Browser To Use
RAND_BROWSER = 9999
NO_BROWSER = 0

CHROME_ID = 1
FIREFOX_ID = 2

# Browser Binaries/Executables Locations
CHROME_BINARY_LOCATION = r"/bin/google-chrome-stable"
FIREFOX_BINARY_LOCATION = r"/opt/firefox/firefox"

# Site Values
SITE_DOMAIN = "finnsec.us"
AD_PROVIDERS = ["propeller_ads"]
# Attribute And Name Of Class
AD_ATTR = ["class"]
AD_ATTR_NAME = "image-block"
# Attribute And Name Of Button To Close Class
AD_CLOSE_ATTR = ["class"]
AD_CLOSE_ATTR_NAME = ["btoa"]

