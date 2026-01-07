
import os
from scripts_playwright import single_page_script, response_script
from scripts_data import data_sightmap


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

FOLDER_NAME = "TheLangston"
APT_NAME = FOLDER_NAME.lower()

BASE_URL = "https://www.livethelangston.com/"
MAIN_URL = "https://livethelangston.securecafe.com/onlineleasing/langston0/availableunits.aspx?myOlePropertyId=1888891"

MAIN_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/PlaywrightOutputs"
os.makedirs(MAIN_DIR, exist_ok=True)

HTML_DIR = f"{MAIN_DIR}/HTML/{FOLDER_NAME}"
os.makedirs(HTML_DIR, exist_ok=True)

DATA_DIR = f"{MAIN_DIR}/Data"
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_CSV_FILE = f"{DATA_DIR}/{APT_NAME}.csv"
MAIN_HTML_FILE = f"{HTML_DIR}/{APT_NAME}.html"


# -----------------------------------------------------------------------------------
# Get HTML (Main)
# -----------------------------------------------------------------------------------

single_page_script(MAIN_URL, MAIN_HTML_FILE)


# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

# data_sightmap(MAIN_JSON_FILE, MAIN_CSV_FILE)
