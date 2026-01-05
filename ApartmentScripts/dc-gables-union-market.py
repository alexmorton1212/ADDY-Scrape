
import subprocess
import os
import re
from reusablescripts import gables_script, gables_get_data


# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "gablesunionmarket"
FOLDER_NAME = "GablesUnionMarket"

BASE_URL = "https://www.gables.com/unionmarket"
MAIN_URL = "https://www.gables.com/unionmarket#floor-plans"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + "_next.html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Get HTML (Floorplan Details)
# ===============================================================

main_script = gables_script(MAIN_URL, OUTPUT_DIR, APT_NAME)
subprocess.run(["osascript", "-e", main_script])


# ===============================================================
# Get Data (Floorplan Details)
# ===============================================================

pattern = re.compile(rf"^{re.escape(APT_NAME)}_\d+_\d+\.html$")
gables_get_data(OUTPUT_DIR, MAIN_CSV_FILE, pattern)
