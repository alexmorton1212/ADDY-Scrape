
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
from reusablescripts import landing_script


# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "westendresidences"
FOLDER_NAME = "WestEndResidences"

BASE_URL = "https://www.westendresidencesdc.com"
MAIN_URL = "https://www.westendresidencesdc.com/floorplans"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"

# ===============================================================
# Get HTML (Main)
# ===============================================================

main_script = landing_script(MAIN_URL, MAIN_HTML_FILE)
# subprocess.run(["osascript", "-e", main_script])

# ===============================================================
# Get URLs (Floorplan Details)
# ===============================================================

links = []

with open(MAIN_HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
    soup = BeautifulSoup(f, "lxml")

for a in soup.select("a.floorplan-action-button[name='applynow']"):
    href = a.get("href")
    if href: links.append(href)

# ===============================================================
# Get HTML (Floorplan Details)
# ===============================================================

for i, url in enumerate(links, start=1):

    index_file_name = OUTPUT_DIR + APT_NAME + "_" + str(i) + ".html"
    i_script = landing_script(url, index_file_name)
    # subprocess.run(["osascript", "-e", i_script])

# ===============================================================
# Get Data (Floorplan Details)
# ===============================================================

rows = []
pattern = re.compile(r"^westendresidences_\d+\.html$")

for filename in os.listdir(OUTPUT_DIR):

    if not pattern.match(filename):
        continue

    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    # loop floorplans (ex: One Bedroom)
    for fp in soup.select("div.floorplan-section"):

        floorplan = fp.get("data-name")

        # loop units
        for tr in fp.select("tr.unit-container"):

            # UNIT NUMBER
            td = tr.select_one("td.td-card-name")
            unit = next(
                t.strip().replace("#", "")
                for t in td.stripped_strings
                if t.startswith("#")
            )

            # SQFT
            td = tr.select_one("td.td-card-sqft")
            sqft = td.contents[-1].strip()

            # RENT
            td = tr.select_one("td.td-card-rent")
            rent_text = td.get_text(" ", strip=True)
            rents = re.findall(r"\$([\d,]+)", rent_text)
            rent_min = int(rents[0].replace(",", ""))

            # AMENITIES
            amenities = ", ".join(
                li.get_text(strip=True)
                for li in tr.select("td.td-card-details li")
            )

            # AVAILABLE DATE
            td = tr.select_one("td.td-card-available")
            available = td.contents[-1].strip()
            if available.lower() == "available": available = "Now"

            rows.append({
                "unit_number": unit,
                "floorplan_name": floorplan,
                "available_date": available,
                "starting_rent": rent_min,
                "square_feet": sqft,
                "building_number": None,
                "amenities": amenities,
                "specials": None
            })

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)