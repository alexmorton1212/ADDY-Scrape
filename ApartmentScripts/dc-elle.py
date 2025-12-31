
import subprocess
import time
import random
import glob
import os
import pandas as pd
from bs4 import BeautifulSoup
import re
import json
from datetime import date


# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "elle"
FOLDER_NAME = "Elle"

BASE_URL = "https://www.elleapartments.com"
MAIN_URL = "https://www.elleapartments.com/floor-plans/"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Helper Functions
# ===============================================================

def run_script(url, output_dir, base_name):

    return f'''
    set pageNum to 1

    tell application "Google Chrome"
        activate
        open location "{url}"
    end tell

    delay 7

    repeat
        tell application "Google Chrome"
            set html to execute front window's active tab javascript "
                document.documentElement.outerHTML
            "
        end tell

        set filePath to "{output_dir}" & "{base_name}_" & pageNum & ".html"
        set f to open for access POSIX file filePath with write permission
        write html to f
        close access f

        tell application "Google Chrome"
            set hasNext to execute front window's active tab javascript "
                (function() {{
                    return document.querySelector('li.next a') ? 'YES' : 'NO';
                }})();
            "
        end tell

        if hasNext is "NO" then
            exit repeat
        end if

        tell application "Google Chrome"
            tell front window's active tab
                execute javascript "
                    var next = document.querySelector('li.next a');
                    if (next) next.click();
                "
            end tell
        end tell

        set pageNum to pageNum + 1
        delay 6
    end repeat

    tell application "Google Chrome"
        close active tab of front window
    end tell
    '''

# ===============================================================
# Get HTML (Floorplan Details)
# ===============================================================

main_script = run_script(MAIN_URL, OUTPUT_DIR, APT_NAME)
subprocess.run(["osascript", "-e", main_script])


# ===============================================================
# Get Data (Floorplan Details)
# ===============================================================

rows = []
pattern = re.compile(r"^elle_\d+\.html$")

for filename in os.listdir(OUTPUT_DIR):

    if not pattern.match(filename): continue
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    listings = soup.select("div.fp-listing-item")

    for item in listings:

        # unit number
        unit_number = item.select_one("h3")
        unit_number = unit_number.get_text(strip=True) if unit_number else None

        # floorplan name (from data attribute)
        fp_link = item.select_one("a.rfwa-fee-calculator")
        floorplan_name = fp_link.get("data-fp-name") if fp_link else None

        # available date
        available_date = fp_link.get("data-available") if fp_link else None
        if available_date: available_date = available_date.replace("Available ", "").strip()

        # base rent
        base_rent = item.select_one("span.base-rent")
        base_rent = base_rent.get_text(strip=True) if base_rent else None
        if base_rent: base_rent = base_rent.replace("base rent", "").strip()

        # square footage
        sqft = item.select_one("p[itemprop='floorSize']")
        sqft = sqft.get_text(strip=True) if sqft else None
        if sqft: sqft = sqft.replace("SQ FT", "").strip()

        rows.append({
            "unit_number": unit_number,
            "floorplan_name": floorplan_name,
            "available_date": available_date,
            "base_rent": base_rent,
            "square_feet": sqft
        })

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)