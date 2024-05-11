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
PROXY_PRODUCT = "smartproxy.com"
PROXY_GEO_TARGET_AREA = "city"
PROXY_SESSION_DURATION = 2
PROXY_GEO_TARGETS_CITIES = {
    "new-york": "us-city-new_york",
    "los-angeles": "us-city-los_angeles",
    "chicago": "us-city-chicago",
    "houston": "us-city-houston",
    "miami": "us-city-miami",
    "london": "uk-city-london",
    "berlin": "de-city-berlin",
    "moscow": "ru-city-moscow",
    "san-francisco": "us-city-san_francisco",
    "boston": "us-city-boston",
    "phoenix": "us-city-phoenix",
    "philadelphia": "us-city-philadelphia",
    "san-antonio": "us-city-san_antonio",
    "san-diego": "us-city-san_diego",
    "san-jose": "us-city-san_jose",
    "mexico": "mx-city-mexico",
    "istanbul": "tr-city-istanbul",
    "madrid": "es-city-madrid",
    "kyiv": "ua-city-kyiv",
    "rome": "it-city-rome",
    "paris": "fr-city-paris",
    "vienna": "at-city-vienna",
    "barcelona": "es-city-barcelona",
    "milan": "it-city-milan",
    "são-paulo": "br-city-são_paulo",
    "lima": "pe-city-lima",
    "bogotá": "co-city-bogotá",
    "rio-de-janeiro": "br-city-rio_de_janeiro",
    "santiago": "cl-city-santiago",
    "caracas": "ve-city-caracas",
    "buenos-aires": "ar-city-buenos_aires",
    "brasília": "br-city-brasília",
    "tokyo": "jp-city-tokyo",
    "bangkok": "th-city-bangkok",
    "seoul": "kr-city-seoul",
    "taipei": "tw-city-taipei",
    "mumbai": "in-city-mumbai",
    "osaka": "jp-city-osaka",
    "hong-kong": "hk-city-hong_kong",
    "shanghai": "cn-city-shanghai",
    "delhi": "in-city-delhi",
    "sydney": "au-city-sydney",
    "helsinki": "fi-city-helsinki",
    "manchester": "uk-city-manchester",
    "central": "hk-city-central",
    "birmingham": "uk-city-birmingham",
    "melbourne": "au-city-melbourne",
    "bristol": "uk-city-bristol",
    "hyderabad": "in-city-hyderabad",
    "bengaluru": "in-city-bengaluru",
    "kolkata": "in-city-kolkata",
    "brisbane": "au-city-brisbane",
    "chennai": "in-city-chennai",
    "zurich": "ch-city-zurich",
    "nottingham": "uk-city-nottingham",
    "dublin": "ie-city-dublin",
    "ho-chi-minh-city": "vn-city-ho_chi_minh_city",
    "jakarta": "id-city-jakarta",
    "glasgow": "uk-city-glasgow",
    "leicester": "uk-city-leicester",
    "liverpool": "gb-city-liverpool",
    "leeds": "gb-city-leeds",
    "queens": "us-city-queens",
    "ashburn": "us-city-ashburn",
    "brooklyn": "us-city-brooklyn",
    "perth": "au-city-perth",
    "sheffield": "gb-city-sheffield",
    "quezon_city": "ph-city-quezon_city",
    "geneva": "ch-city-geneva",
    "pune": "in-city-pune",
    "hanoi": "vn-city-hanoi",
    "brussels": "be-city-brussels",
    "charlotte": "us-city-charlotte",
    "nairobi": "ke-city-nairobi",
    "zagreb": "hr-city-zagreb",
    "edmonton": "ca-city-edmonton",
    "fort_worth": "us-city-fort_worth",
    "guayaquil": "ec-city-guayaquil",
    "recife": "br-city-recife",
    "macao": "mo-city-macao",
    "riga": "lv-city-riga",
    "riyadh": "sa-city-riyadh",
    "turin": "it-city-turin",
    "san_salvador": "sv-city-san_salvador",
    "winnipeg": "ca-city-winnipeg",
    "sofia": "bg-city-sofia",
    "phnom_penh": "kh-city-phnom_penh",
    "düsseldorf": "de-city-düsseldorf",
    "montevideo": "uy-city-montevideo",
    "vancouver": "ca-city-vancouver",
    "columbus": "us-city-columbus",
    "cleveland": "us-city-cleveland",
    "bishkek": "kg-city-bishkek",
    "indianapolis": "us-city-indianapolis",
    "kowloon": "hk-city-kowloon",
    "goiânia": "br-city-goiânia",
    "gothenburg": "se-city-gothenburg",
    "naples": "it-city-naples",
    "sacramento": "us-city-sacramento",
    "chandigarh": "in-city-chandigarh",
    "tainan_city": "tw-city-tainan_city",
    "dhaka": "bd-city-dhaka",
    "pittsburgh": "us-city-pittsburgh",
    "tashkent": "uz-city-tashkent",
    "kuwait_city": "kw-city-kuwait_city",
    "scarborough": "ca-city-scarborough",
    "san_jose": "cr-city-san_jose",
    "lisbon": "pt-city-lisbon",
    "surrey": "ca-city-surrey",
    "palermo": "it-city-palermo",
    "jeddah": "sa-city-jeddah",
    "ludhiana": "in-city-ludhiana",
    "frankfurt_am_main": "de-city-frankfurt_am_main",
    "buffalo": "us-city-buffalo",
    "ulan_bator": "mn-city-ulan_bator",
    "chisinau": "md-city-chisinau",
    "asunción": "py-city-asunción",
    "bridgetown": "bb-city-bridgetown",
    "Kansas City": "us-city-kansas_city",
    "Irving": "us-city-irving",
    "Santiago de Cali": "co-city-santiago_de_cali",
    "Sapporo": "jp-city-sapporo",
    "Konya": "tr-city-konya",
    "Bekasi": "id-city-bekasi",
    "Kingston": "jm-city-kingston",
    "Accra": "gh-city-accra",
    "Newark": "us-city-newark",
    "Bacoor": "ph-city-bacoor",
    "Poznan": "pl-city-poznan",
    "St Louis": "us-city-st_louis",
    "Colorado Springs": "us-city-colorado_springs",
    "Antwerp": "be-city-antwerp",
    "Cagayan de Oro": "ph-city-cagayan_de_oro",
    "Mississauga": "ca-city-mississauga",
    "Fort Lauderdale": "us-city-fort_lauderdale",
    "Angeles City": "ph-city-angeles_city",
    "Lincoln": "us-city-lincoln",
    "Bhopal": "in-city-bhopal",
    "Staten Island": "us-city-staten_island",
    "Managua": "ni-city-managua",
    "Bursa": "tr-city-bursa",
    "Medan": "id-city-medan",
    "Córdoba": "ar-city-córdoba",
    "Arlington": "us-city-arlington",
    "Belém": "br-city-belém",
    "Lyon": "fr-city-lyon",
    "Semarang": "id-city-semarang",
    "Tel Aviv": "il-city-tel_aviv",
    "Toronto": "ca-city-toronto",
    "Oslo": "no-city-oslo",
    "North York": "ca-city-north_york",
    "Amsterdam": "nl-city-amsterdam",
    "Quebec": "ca-city-quebec",
    "Hialeah": "us-city-hialeah",
    "Wroclaw": "pl-city-wroclaw",
    "Natal": "br-city-natal",
    "Lagos": "ng-city-lagos",
    "Taoyuan District": "tw-city-taoyuan_district",
    "Guarulhos": "br-city-guarulhos",
    "Milwaukee": "us-city-milwaukee",
    "Fukuoka": "jp-city-fukuoka",
    "Umeda": "jp-city-umeda",
    "Louisville": "us-city-louisville",
    "Porto Alegre": "br-city-porto_alegre",
    "Campinas": "br-city-campinas",
    "Karachi": "pk-city-karachi",
}

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
