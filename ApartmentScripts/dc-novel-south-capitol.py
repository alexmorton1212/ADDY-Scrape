
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
from reusablescripts import landing_script, sightmap_horizontal_script


# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "novelsouthcapitol"
FOLDER_NAME = "NovelSouthCapitol"

BASE_URL = "https://www.novelsouthcapitol.com"
MAIN_URL = "https://www.novelsouthcapitol.com/floor-plans"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Get HTML (Main)
# ===============================================================

first_url = "https://floorplans.novelsouthcapitol.com/"

main_script = landing_script(first_url, MAIN_HTML_FILE)
subprocess.run(["osascript", "-e", main_script])

# ===============================================================
# Get URL (Sightmap)
# ===============================================================

with open(MAIN_HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
    soup = BeautifulSoup(f, "lxml")

iframe = soup.find("iframe", src=lambda s: s and "sightmap.com/embed" in s)
embed_url = iframe["src"] if iframe else None

# ===============================================================
# Get HTML (Sightmap)
# ===============================================================

main_sightmap_script = sightmap_horizontal_script(embed_url, OUTPUT_DIR, APT_NAME)
subprocess.run(["osascript", "-e", main_sightmap_script])

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

    unit_list = soup.select_one('ul[data-testid="unit-list"]')
    if not unit_list: continue

    for btn in unit_list.select("button"):
        text = btn.get_text(" ", strip=True)
        
        # unit number
        unit_number_match = re.search(r"APT\s+([A-Z0-9]+)", text)
        unit_number = unit_number_match.group(1) if unit_number_match else None

        # floorplan name
        fp_span = btn.select_one("span.css-y52d0e")
        floorplan_name = fp_span.get_text(strip=True) if fp_span else None

        # building (East / West / etc.)
        building_number = None
        if floorplan_name:
            m = re.search(r"\s+(East|West|North|South)\b$", floorplan_name)
            if m:
                building_number = m.group(1)
                floorplan_name = floorplan_name[:m.start()].strip()

        # square footage
        sqft_match = re.search(r"([\d,]+)\s*sq\.?\s*ft", text, re.I)
        square_footage = sqft_match.group(1).replace(",", "") if sqft_match else None

        # availability
        avail_match = re.search(r"Available\s+(Now|[A-Za-z]+\s+\d+\w*)", text)
        available_date = avail_match.group(1) if avail_match else None

        # starting rent
        rent_match = re.search(r"\$([\d,]+)\s*/mo", text)
        starting_rent = rent_match.group(1).replace(",", "") if rent_match else None

        rows.append({
            "unit_number": unit_number,
            "floorplan_name": floorplan_name,
            "available_date": available_date,
            "starting_rent": starting_rent,
            "square_feet": square_footage,
            "building_number": building_number,
            "amenities": None,
            "specials": None
        })

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)