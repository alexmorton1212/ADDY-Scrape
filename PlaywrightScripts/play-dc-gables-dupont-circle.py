
import os
from scripts_playwright import response_script
from scripts_data import data_knock


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

FOLDER_NAME = "GablesDupontCircle"

MAIN_URL = "https://www.gables.com/dupontcircle#floor-plans"

MAIN_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/PlaywrightOutputs"
os.makedirs(MAIN_DIR, exist_ok=True)

HTML_DIR = f"{MAIN_DIR}/HTML/{FOLDER_NAME}"
os.makedirs(HTML_DIR, exist_ok=True)

DATA_DIR = f"{MAIN_DIR}/Data"
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_JSON_FILE = f"{HTML_DIR}/{FOLDER_NAME.lower()}.json"
MAIN_CSV_FILE = f"{DATA_DIR}/{FOLDER_NAME.lower()}.csv"


# -----------------------------------------------------------------------------------
# Response URL Matching
# -----------------------------------------------------------------------------------

def response_criteria(response):
    url = response.url.lower()
    return (
        "doorway-api" in url
        and "knockrentals" in url
        and "units" in url
    )

# -----------------------------------------------------------------------------------
# Batch Entrypoint
# -----------------------------------------------------------------------------------

def run():
    response_script(MAIN_URL, MAIN_JSON_FILE, response_criteria)
    data_knock(MAIN_JSON_FILE, MAIN_CSV_FILE)


# -----------------------------------------------------------------------------------
# Run Standalone
# -----------------------------------------------------------------------------------

if __name__ == "__main__": run()

def dc_1_main_gablesdupontcircle():
    return True

def dc_1_sub_gablesdupontcircle(sub_url):
    return sub_url