

import subprocess
import os
import pandas as pd
from bs4 import BeautifulSoup
import re
from reusablescripts import engrain_get_labels, engrain_script

# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "theiris"
FOLDER_NAME = "TheIris"

BASE_URL = "https://theirisdc.com"
MAIN_URL = "https://theirisdc.com/floorplans/"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Get Floors Available
# ===============================================================

floor_script = engrain_get_labels(MAIN_URL)
result = subprocess.run(["osascript", "-e", floor_script], capture_output=True, text=True)
floor_labels = result.stdout.strip().split(",")


# ===============================================================
# Get HTML (Floorplan Details)
# ===============================================================

big_script = engrain_script(OUTPUT_DIR, floor_labels, APT_NAME)
subprocess.run(["osascript", "-e", big_script], capture_output=True, text=True)


# ===============================================================
# Get Data (Floorplan Details)
# ===============================================================

rows = []
pattern = re.compile(rf"^{re.escape(APT_NAME)}_.+\.html$")

for filename in os.listdir(OUTPUT_DIR):

    if not pattern.match(filename): continue
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    for card in soup.select('a[data-jd-fp-selector="unit-card"]'):

        # FLOORPLAN
        floorplan = card.select_one(".jd-fp-unit-card__floorplan-title span").get_text(strip=True)

        # UNIT NUMBER
        unit = card.select_one(".jd-fp-card-info__title--large").get_text(strip=True).replace("#", "")

        # AVAILABILITY
        avail_raw = card.select_one(".jd-fp-card-info__text--brand").get_text(strip=True)
        availability = ("Now" if "Now" in avail_raw else avail_raw.replace("Available ", ""))

        # STARTING PRICE
        price_text = card.select_one(".jd-fp-card-info-term-and-base--base").get_text()
        price = int(re.search(r"\$([\d,]+)", price_text).group(1).replace(",", ""))

        # SQFT
        details = card.select_one("p.jd-fp-card-info__text").get_text(" ", strip=True)
        sqft = int(re.search(r"(\d+)\s*sq", details, re.I).group(1))

        rows.append({
            "unit_number": unit,
            "floorplan_name": floorplan,
            "available_date": availability,
            "starting_rent": price,
            "square_feet": sqft,
            "building_number": None,
            "amenities": None,
            "specials": None
        })    

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)
