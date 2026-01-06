
import os
from scripts_playwright import response_script
from scripts_data import data_sightmap


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

FOLDER_NAME = "TheLouis"
APT_NAME = FOLDER_NAME.lower()

BASE_URL = "https://thelouisdc.com"
MAIN_URL = "https://thelouisdc.com/floorplans/"

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
        "sightmap" in url
        and "api" in url
        and "sightmaps" in url
    )

response_script(MAIN_URL, MAIN_JSON_FILE, response_criteria)


# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

data_sightmap(MAIN_JSON_FILE, MAIN_CSV_FILE)