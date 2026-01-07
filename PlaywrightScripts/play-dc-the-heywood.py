
import os
from scripts_playwright import response_script
from scripts_data import data_wydown


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

FOLDER_NAME = "TheHeywood"
APT_NAME = FOLDER_NAME.lower()

BASE_URL = "https://www.wydownpm.com/our-properties/the-heywood"
MAIN_URL = "https://www.wydownpm.com/our-properties/the-heywood#Availability-Property"

MAIN_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/PlaywrightOutputs"
os.makedirs(MAIN_DIR, exist_ok=True)

HTML_DIR = f"{MAIN_DIR}/HTML/{FOLDER_NAME}"
os.makedirs(HTML_DIR, exist_ok=True)

DATA_DIR = f"{MAIN_DIR}/Data"
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_JSON_FILE = f"{HTML_DIR}/{APT_NAME}.json"
MAIN_CSV_FILE = f"{DATA_DIR}/{APT_NAME}.csv"

JSON_SEARCH_NAME = "the heywood"


# -----------------------------------------------------------------------------------
# Get HTML (Main)
# -----------------------------------------------------------------------------------

def response_criteria(response):
    url = response.url.lower()
    return (
        "public" in url
        and "appfolio-listings" in url
        and "data" in url
    )

response_script(MAIN_URL, MAIN_JSON_FILE, response_criteria)


# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

data_wydown(MAIN_JSON_FILE, MAIN_CSV_FILE, JSON_SEARCH_NAME)
