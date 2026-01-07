
import os
from scripts_playwright import capture_floorplan_pages, single_page_script


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

FOLDER_NAME = "Wren"
APT_NAME = FOLDER_NAME.lower()

BASE_URL = "https://www.thewrendc.com"
# MAIN_URL = "https://www.thewrendc.com/floorplans"
# MAIN_URL = "https://www.thewrendc.com/floorplans/1-bedroom---1-bath-|-a03"
MAIN_URL = "https://www.rentcafe.com/apartments/dc/washington/the-wren/default.aspx"

MAIN_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/PlaywrightOutputs"
os.makedirs(MAIN_DIR, exist_ok=True)

HTML_DIR = f"{MAIN_DIR}/HTML/{FOLDER_NAME}"
os.makedirs(HTML_DIR, exist_ok=True)

DATA_DIR = f"{MAIN_DIR}/Data"
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_HTML_FILE = f"{HTML_DIR}/{APT_NAME}.html"
MAIN_CSV_FILE = f"{DATA_DIR}/{APT_NAME}.csv"


# -----------------------------------------------------------------------------------
# Get HTML (Main)
# -----------------------------------------------------------------------------------

# capture_floorplan_pages(MAIN_URL, MAIN_HTML_FILE)
single_page_script(MAIN_URL, MAIN_HTML_FILE)

# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------
