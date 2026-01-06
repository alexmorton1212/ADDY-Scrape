
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from scripts_playwright import paginated_navigation_script


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "thewray"
FOLDER_NAME = "TheWray"

BASE_URL = "https://www.thewraydc.com/"
MAIN_URL = "https://www.thewraydc.com/floor-plans/"

MAIN_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/PlaywrightOutputs"
os.makedirs(MAIN_DIR, exist_ok=True)

HTML_DIR = f"{MAIN_DIR}/HTML/{FOLDER_NAME}"
os.makedirs(HTML_DIR, exist_ok=True)

DATA_DIR = f"{MAIN_DIR}/Data"
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_HTML_FILE = f"{HTML_DIR}/{APT_NAME}.html"
MAIN_CSV_FILE = f"{DATA_DIR}/{APT_NAME}.csv"


# -----------------------------------------------------------------------------------
# Get HTML (Floorplan Details)
# -----------------------------------------------------------------------------------

has_next = """
(function () {
    var nextLink = document.querySelector('.pagination a:has(span.pag_next)');
    return !!nextLink;
})();
"""

go_next = """
(function () {
    var nextLink = document.querySelector('.pagination a:has(span.pag_next)');
    if (nextLink) { window.location.href = nextLink.href; }
})();
"""

paginated_navigation_script(MAIN_URL, HTML_DIR, APT_NAME, has_next, go_next)


# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------==

rows = []
pattern = re.compile(rf"^{re.escape(APT_NAME)}_\d+\.html$")

for filename in os.listdir(HTML_DIR):

    if not pattern.match(filename): continue
    path = os.path.join(HTML_DIR, filename)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    for block in soup.select("div.block"):

         # unit number
        unit = block.select_one("h2.fp_unit_num")
        unit_number = unit.get_text(strip=True) if unit else None
        if unit_number: unit_number = unit_number.replace("residence", "").strip()

        # square footage
        sqft = block.select_one("div[itemprop='floorSize']")
        square_feet = None
        if sqft:
            text = sqft.get_text(" ", strip=True)
            for part in text.split():
                if part.isdigit():
                    square_feet = part
                    break

        # base rent
        price_block = block.select_one("div.fp_unit_detail span")
        rent = price_block.get_text(strip=True) if price_block else None
        if rent: rent = rent.replace("/ Month", "").strip()

        # available date
        availability = None
        detail_divs = block.select("div.fp_unit_detail")
        if len(detail_divs) > 1:
            text = detail_divs[1].get_text(" ", strip=True)
            if "Available" in text:
                availability = text.split("Available")[-1].replace(":", "").strip()

        rows.append({
            "unit_number": unit_number,
            "floorplan_name": None,
            "available_date": availability,
            "starting_rent": rent,
            "square_feet": square_feet,
            "building_number": None,
            "amenities": None,
            "specials": None
        })

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)
