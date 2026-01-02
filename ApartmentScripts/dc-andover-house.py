
import subprocess
import os
from reusablescripts import landing_script, udr_get_data


# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "andoverhouse"
FOLDER_NAME = "AndoverHouse"

BASE_URL = "https://www.udr.com/washington-dc-apartments/thomas-circle/andover-house/"
MAIN_URL = "https://www.udr.com/washington-dc-apartments/thomas-circle/andover-house/apartments-pricing/"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Get HTML (Main)
# ===============================================================

first_script = landing_script(MAIN_URL, MAIN_HTML_FILE)
subprocess.run(["osascript", "-e", first_script])


# ===============================================================
# Get Data (Floorplan Details)
# ===============================================================

udr_get_data(MAIN_HTML_FILE, MAIN_CSV_FILE)
