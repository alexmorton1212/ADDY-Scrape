
import os
from scripts_playwright import response_script
from scripts_data import data_gables


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "gablesdupontcircle"
FOLDER_NAME = "GablesDupontCircle"

BASE_URL = "https://www.gables.com/dupontcircle"
MAIN_URL = "https://www.gables.com/dupontcircle#floor-plans"

MAIN_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/PlaywrightOutputs"
os.makedirs(MAIN_DIR, exist_ok=True)

HTML_DIR = f"{MAIN_DIR}/HTML/{FOLDER_NAME}"
os.makedirs(HTML_DIR, exist_ok=True)

DATA_DIR = f"{MAIN_DIR}/Data"
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_JSON_FILE = f"{HTML_DIR}/{APT_NAME}.json"
MAIN_CSV_FILE = f"{DATA_DIR}/{APT_NAME}.csv"


# -----------------------------------------------------------------------------------
# Get HTML (Main)
# -----------------------------------------------------------------------------------

def response_criteria(response):
    url = response.url.lower()
    return (
        "doorway-api" in url
        and "property" in url
        and "units" in url
    )

response_script(MAIN_URL, MAIN_JSON_FILE, response_criteria)


# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

data_gables(MAIN_JSON_FILE, MAIN_CSV_FILE)