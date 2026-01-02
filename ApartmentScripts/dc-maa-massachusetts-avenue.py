
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

APT_NAME = "maamassachusettsavenue"
FOLDER_NAME = "MAAMassachusettsAvenue"

BASE_URL = "https://www.maac.com/district-of-columbia/washington-dc/maa-massachusetts-avenue/"
MAIN_URL = "https://www.maac.com/district-of-columbia/washington-dc/maa-massachusetts-avenue/"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Get HTML (Main)
# ===============================================================

main_script = landing_script(MAIN_URL, MAIN_HTML_FILE)
subprocess.run(["osascript", "-e", main_script])


# ===============================================================
# Get Data (Floorplan Details)
# ===============================================================

rows = []

with open(MAIN_HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
    soup = BeautifulSoup(f, "lxml")

for apt in soup.select("div.available-apartments__body > div.available-apartments__body--apt"):

    # FLOORPLAN NAME → "1 Bed, 1 Bath"
    details_items = apt.select(".apt-details ul li")
    floorplan = details_items[0].get_text(strip=True)

    # UNIT NUMBER
    unit_text = apt.select_one("span.unit").get_text(strip=True)
    unit_number = unit_text.replace("Unit #", "").strip()

    # STARTING PRICE
    price_text = apt.select_one("span.price").get_text(strip=True)
    starting_price = int(price_text.replace("$", "").replace(",", ""))

    # SQFT (second li in details list)
    details_items = apt.select(".apt-details ul li")
    sqft_text = details_items[1].get_text(strip=True)  # e.g. "1025 Sq. Ft."
    square_feet = int(sqft_text.split()[0])

    # AVAILABILITY (from "Move-in: 01/01 - 01/04")
    move_in_text = next(
        li.get_text(" ", strip=True)
        for li in details_items
        if "Move-in:" in li.get_text()
    )
    availability = re.search(r"Move-in:\s*(\d{2}/\d{2})", move_in_text).group(1)

    # AMENITIES (already comma-separated)
    amenities = apt.select_one(".apt-amenities").get_text(" ", strip=True)

    rows.append({
        "unit_number": unit_number,
        "available_date": availability,
        "starting_rent": starting_price,
        "square_feet": square_feet,
        "building_number": None,
        "amenities": amenities,
        "specials": None
    })    

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)
