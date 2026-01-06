
import os
from scripts_playwright import single_page_script
from scripts_data import data_udr


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "1301thomascircle"
FOLDER_NAME = "1301ThomasCircle"

BASE_URL = "https://www.udr.com/washington-dc-apartments/logan-circle/1301-thomas-circle"
MAIN_URL = "https://www.udr.com/washington-dc-apartments/logan-circle/1301-thomas-circle/apartments-pricing/"

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

single_page_script(MAIN_URL, MAIN_HTML_FILE)


# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

data_udr(MAIN_HTML_FILE, MAIN_CSV_FILE)