
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

APT_NAME = "westend25"
FOLDER_NAME = "WestEnd25"

BASE_URL = "https://www.westend25apts.com"
MAIN_URL = "https://www.westend25apts.com/washington/westend-25/conventional/"

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

with open(MAIN_HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
    soup = BeautifulSoup(f, "lxml")

units_js = next(
    s.string for s in soup.find_all("script")
    if s.string and "var unitsData" in s.string
)

units_js = (
    units_js
    .replace("var unitsData =", "")
    .strip()
    .rstrip(";")
    .strip("'")
    .encode("utf-8")
    .decode("unicode_escape")
)

units_data = json.loads(units_js)

rows = [
    {
        "unit_number": u.get("unit_number"),
        "floorplan_name": u.get("floorplan_name"),
        "available_date": u.get("available_on"),
        "starting_rent": u.get("min_rent"),
        "square_feet": u.get("sqft_unit") or u.get("sqft"),
        "building_number": None
    }
    for units in units_data.values()
    for u in units
]

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)