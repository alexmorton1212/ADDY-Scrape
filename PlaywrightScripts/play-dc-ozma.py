
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from scripts_playwright import paginated_navigation_script


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "ozma"
FOLDER_NAME = "Ozma"

BASE_URL = "https://www.ozmanoma.com"
MAIN_URL = "https://www.ozmanoma.com/floorplans/"

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
    var next = document.querySelector('.fp-content-navbar-pagination.next span[data-page]');
    return !!next;
})();
"""

go_next = """
(function () {
    var next = document.querySelector('.fp-content-navbar-pagination.next span[data-page]');
    if (next) { next.click(); }
})();
"""

paginated_navigation_script(MAIN_URL, HTML_DIR, APT_NAME, has_next, go_next)


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

    listings = soup.select("div.fp-block")

    for item in listings:

        meta = item.select_one("div.fp-meta")

        # unit number
        unit_number = meta.select_one("div > strong").get_text(strip=True)

        # floorplan name
        bed = meta.select("div")[1].select("span")[0].get_text(strip=True)
        bath = meta.select("div")[1].select("span")[1].get_text(strip=True)
        floorplan_name = f"{bed} | {bath}"

        # sqft
        sqft_text = meta.select("div")[2].get_text(" ", strip=True)
        square_feet = int(re.search(r"(\d+)\s*SF", sqft_text).group(1))

        # starting rent
        rent_text = meta.select("div")[3].get_text(" ", strip=True)
        starting_rent = int(re.search(r"\$([\d,]+)", rent_text).group(1).replace(",", ""))

        # availability
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