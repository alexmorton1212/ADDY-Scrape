
import os
import re
import json
import pandas as pd
from bs4 import BeautifulSoup
from scripts_playwright import single_page_script


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "theshay"
FOLDER_NAME = "TheShay"

BASE_URL = "https://www.theshay.com"
MAIN_URL = "https://www.theshay.com/floorplans"

MAIN_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/PlaywrightOutputs"
os.makedirs(MAIN_DIR, exist_ok=True)

HTML_DIR = f"{MAIN_DIR}/HTML/{FOLDER_NAME}"
os.makedirs(HTML_DIR, exist_ok=True)

DATA_DIR = f"{MAIN_DIR}/Data"
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_HTML_FILE = f"{HTML_DIR}/{APT_NAME}.html"
MAIN_CSV_FILE = f"{DATA_DIR}/{APT_NAME}.csv"


# -----------------------------------------------------------------------------------
# Get HTML (Main)
# -----------------------------------------------------------------------------------

single_page_script(MAIN_URL, MAIN_HTML_FILE)


# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

rows = []

with open(MAIN_HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
    soup = BeautifulSoup(f, "lxml")

for script in soup.find_all("script"):
    if not script.string or "ysi.unitsList" not in script.string:
        continue

    match = re.search(
        r"ysi\.unitsList\s*=\s*(\[\s*.*?\s*\]);",
        script.string,
        re.DOTALL
    )
    if not match:
        continue

    for unit in json.loads(match.group(1)):

        unit_code = unit.get("UnitCode")

        rows.append({
            "unit_number": unit_code,
            "floorplan_name": unit.get("FloorplanName"),
            "available_date": (
                unit.get("AvailableDate").split("T")[0]
                if unit.get("AvailableDate") else None
            ),
            "starting_rent": int(unit["MinRent"]) if unit.get("MinRent") is not None else None,
            "square_feet": int(unit["SqFt"]) if unit.get("SqFt") is not None else None,
            "building_number": (
                "East" if unit_code and unit_code.startswith("E")
                else "West" if unit_code and unit_code.startswith("W")
                else None
            ),
            "amenities": ", ".join(unit.get("Amenities", [])) or None,
            "specials": (
                None if unit.get("HasSpecials") is False
                else unit.get("HasSpecials")
            )
        })

    break

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)