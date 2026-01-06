
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from scripts_playwright import single_page_script


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "maamassachusettsavenue"
FOLDER_NAME = "MAAMassachusettsAvenue"

BASE_URL = "https://www.maac.com/district-of-columbia/washington-dc/maa-massachusetts-avenue/"
MAIN_URL = "https://www.maac.com/district-of-columbia/washington-dc/maa-massachusetts-avenue/"

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

for apt in soup.select("div.available-apartments__body > div.available-apartments__body--apt"):

    # floorplan name
    details_items = apt.select(".apt-details ul li")
    floorplan = details_items[0].get_text(strip=True)

    # unit number
    unit_text = apt.select_one("span.unit").get_text(strip=True)
    unit_number = unit_text.replace("Unit #", "").strip()

    # starting price
    price_text = apt.select_one("span.price").get_text(strip=True)
    starting_price = int(price_text.replace("$", "").replace(",", ""))

    # sqft
    details_items = apt.select(".apt-details ul li")
    sqft_text = details_items[1].get_text(strip=True)
    square_feet = int(sqft_text.split()[0])

    # availability
    move_in_text = next(
        li.get_text(" ", strip=True)
        for li in details_items
        if "Move-in:" in li.get_text()
    )
    availability = re.search(r"Move-in:\s*(\d{2}/\d{2})", move_in_text).group(1)

    # amenities
    amenities = apt.select_one(".apt-amenities").get_text(" ", strip=True)

    rows.append({
        "unit_number": unit_number,
        "floorplan_name": floorplan,
        "available_date": availability,
        "starting_rent": starting_price,
        "square_feet": square_feet,
        "building_number": None,
        "amenities": amenities,
        "specials": None
    })    

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)