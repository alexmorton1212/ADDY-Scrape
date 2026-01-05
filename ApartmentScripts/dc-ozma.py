
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
from reusablescripts import paginated_script, landing_script


# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "ozma"
FOLDER_NAME = "Ozma"

BASE_URL = "https://www.ozmanoma.com"
MAIN_URL = "https://www.ozmanoma.com/floorplans/"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Get HTML (Floorplan Details)
# ===============================================================

has_next = """
(function () {
    var next = document.querySelector('.fp-content-navbar-pagination.next span[data-page]');
    return next ? 'YES' : '';
})();
"""

go_next = """
var next = document.querySelector('.fp-content-navbar-pagination.next span[data-page]');
if (next) next.click();
"""

main_script = paginated_script(MAIN_URL, OUTPUT_DIR, APT_NAME, has_next, go_next)
# subprocess.run(["osascript", "-e", main_script])


# ===============================================================
# Get Data (Floorplan Details)
# ===============================================================

rows = []
pattern = re.compile(rf"^{re.escape(APT_NAME)}_\d+\.html$")

for filename in os.listdir(OUTPUT_DIR):

    if not pattern.match(filename): continue
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    listings = soup.select("div.fp-block")

    for item in listings:

        meta = item.select_one("div.fp-meta")

        # UNIT NUMBER (first strong)
        unit_number = meta.select_one("div > strong").get_text(strip=True)

        # FLOORPLAN NAME (the line with spans and the "|" between them)
        bed = meta.select("div")[1].select("span")[0].get_text(strip=True)
        bath = meta.select("div")[1].select("span")[1].get_text(strip=True)
        floorplan_name = f"{bed} | {bath}"

        # SQFT (e.g., "587 SF")
        sqft_text = meta.select("div")[2].get_text(" ", strip=True)
        square_feet = int(re.search(r"(\d+)\s*SF", sqft_text).group(1))

        # STARTING RENT (e.g., "From $2,233 /mo")
        rent_text = meta.select("div")[3].get_text(" ", strip=True)
        starting_rent = int(re.search(r"\$([\d,]+)", rent_text).group(1).replace(",", ""))

        # AVAILABILITY (two spans: "Available" + " 02.26.2026" OR " Now")
        avail_div = meta.select("div")[4]
        available_date = avail_div.select("span")[1].get_text(strip=True)

        rows.append({
            "unit_number": unit_number,
            "floorplan_name": floorplan_name,
            "available_date": available_date,
            "starting_rent": starting_rent,
            "square_feet": square_feet,
            "building_number": None,
            "amenities": None,
            "specials": None
        })


pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)