

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
from reusablescripts import paginated_script

# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "thewray"
FOLDER_NAME = "TheWray"

BASE_URL = "https://www.thewraydc.com/"
MAIN_URL = "https://www.thewraydc.com/floor-plans/"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Get HTML (Floor Details)
# ===============================================================

has_next = """
(function () {
    var nextLink = document.querySelector('.pagination a:has(span.pag_next)');
    return nextLink ? 'YES' : '';
})();
"""

go_next = """
var nextLink = document.querySelector('.pagination a:has(span.pag_next)');
if (nextLink) window.location.href = nextLink.href;
"""

main_script = paginated_script(MAIN_URL, OUTPUT_DIR, APT_NAME, has_next, go_next)
subprocess.run(["osascript", "-e", main_script])


# ===============================================================
# Get Data (Floor Details)
# ===============================================================

rows = []
pattern = re.compile(rf"^{re.escape(APT_NAME)}_\d+\.html$")

for filename in os.listdir(OUTPUT_DIR):

    if not pattern.match(filename): continue
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    for block in soup.select("div.block"):

         # -------- unit number --------
        unit = block.select_one("h2.fp_unit_num")
        unit_number = unit.get_text(strip=True) if unit else None
        if unit_number: unit_number = unit_number.replace("residence", "").strip()

        # -------- square footage --------
        sqft = block.select_one("div[itemprop='floorSize']")
        square_feet = None
        if sqft:
            # e.g. "Two Bedroom Two Bathroom 706 Square Feet"
            text = sqft.get_text(" ", strip=True)
            for part in text.split():
                if part.isdigit():
                    square_feet = part
                    break

        # -------- rent + availability --------
        price_block = block.select_one("div.fp_unit_detail span")
        rent = price_block.get_text(strip=True) if price_block else None
        if rent: rent = rent.replace("/ Month", "").strip()

        availability = None
        detail_divs = block.select("div.fp_unit_detail")
        if len(detail_divs) > 1:
            text = detail_divs[1].get_text(" ", strip=True)
            # e.g. " $4,391 / Month Available: 02.03.2026"
            if "Available" in text:
                availability = text.split("Available")[-1].replace(":", "").strip()

        rows.append({
            "unit_number": unit_number,
            "floorplan_name": None,
            "available_date": availability,
            "base_rent": rent,
            "square_feet": square_feet
        })

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)