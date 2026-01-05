
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from playwright_scripts import paginated_inplace_script


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "citymarketato"
FOLDER_NAME = "CityMarketAtO"

BASE_URL = "https://www.citymarketato.com"
MAIN_URL = "https://www.citymarketato.com/floor-plans/"

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
    var next = document.querySelector('button.next_page');
    return !!next;
})();
"""

go_next = """
(function () {
    var next = document.querySelector('button.next_page');
    if (next) { next.click(); }
})();
"""

change_signal = """
(function () {
    var current = document.querySelector('.fp_pagination .subhead_2');
    return current ? current.innerText : '';
})();
"""

paginated_inplace_script(MAIN_URL, HTML_DIR, APT_NAME, has_next, go_next, change_signal)


# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

rows = []
pattern = re.compile(rf"^{re.escape(APT_NAME)}_\d+\.html$")

for filename in os.listdir(HTML_DIR):

    if not pattern.match(filename): continue
    path = os.path.join(HTML_DIR, filename)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    listings = soup.select("div.floorplan_grid div.box")

    for item in listings:

        # BUILDING NAME (from logo class)
        logo = item.select_one("div.building_logo")
        building_name = None
        if logo:
            # second class is the building identifier
            classes = logo.get("class", [])
            building_name = next(
                (c for c in classes if c != "building_logo"),
                None
            )
        if building_name == "medley": building_name = "The Medley"
        if building_name == "intersect": building_name = "Intersect"
        if building_name == "eeop": building_name = "880P"

        # UNIT NUMBER
        unit_number = item.select_one("h2.unit_id")
        unit_number = (
            unit_number.get_text(strip=True)
            .replace("Unit", "")
            .strip()
            if unit_number else None
        )

        # DETAILS BLOCK
        details = item.select_one("p.details")
        details_text = details.get_text(" ", strip=True) if details else ""

        # FLOORPLAN NAME (e.g. "Studio / 1 Bath")
        floorplan_name = None
        details = item.select_one("p.details")

        if details:
            first_line = details.contents[0].strip()
            parts = [p.strip() for p in first_line.split("/", 2)]
            if len(parts) >= 2:
                floorplan_name = f"{parts[0]} / {parts[1]}"

        # STARTING RENT
        rent_match = re.search(r"\$([\d,]+)", details_text)
        starting_rent = (
            int(rent_match.group(1).replace(",", ""))
            if rent_match else None
        )

        # SQFT
        sqft_match = re.search(r"(\d+)\s*SF", details_text, re.I)
        square_feet = int(sqft_match.group(1)) if sqft_match else None

        # AVAILABILITY
        avail_match = re.search(r"Available\s+(Now|\d{2}/\d{2}/\d{4})", details_text)
        available_date = avail_match.group(1) if avail_match else None

        rows.append({
            "unit_number": unit_number,
            "floorplan_name": floorplan_name,
            "available_date": available_date,
            "starting_rent": starting_rent,
            "square_feet": square_feet,
            "building_number": building_name,
            "amenities": None,
            "specials": None
        })

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)