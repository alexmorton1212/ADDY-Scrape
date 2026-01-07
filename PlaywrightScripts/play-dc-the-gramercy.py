
import os
from scripts_playwright import single_page_script
from scripts_data import data_udr


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "thegramercy"
FOLDER_NAME = "TheGramercy"

BASE_URL = "https://www.gramercyapts.com"
MAIN_URL = "https://gramercyapts.securecafe.com/onlineleasing/the-gramercy-2/oleapplication.aspx?RCStandardCampaignId_1236432=437778&propleadsource_1236432=portal&stepname=Apartments&myOlePropertyId=1236432"

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

# data_udr(MAIN_HTML_FILE, MAIN_CSV_FILE)