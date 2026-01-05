
import subprocess
import os
import pandas as pd
from bs4 import BeautifulSoup
import re
from reusablescripts import paginated_script


# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "margarite"
FOLDER_NAME = "Margarite"

BASE_URL = "https://margaritedc.com"
MAIN_URL = "https://margaritedc.com/floor-plans/"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Get HTML (Floorplan Details)
# ===============================================================

has_next = """
var nextBtn = document.querySelector('#neodtable_next');
(nextBtn && !nextBtn.classList.contains('disabled')) ? 'YES' : '';
"""

go_next = """
var nextBtn = document.querySelector('#neodtable_next');
if (nextBtn && !nextBtn.classList.contains('disabled')) nextBtn.click();
"""

main_script = paginated_script(MAIN_URL, OUTPUT_DIR, APT_NAME, has_next, go_next)
subprocess.run(["osascript", "-e", main_script])

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

    listings = soup.select("table#neodtable tbody.plan__cards > tr.plan__card")

    for row in listings:

        # -------------------------
        # UNIT NUMBER
        # -------------------------
        unit_number = row.select_one("td.plan__name h5")
        unit_number = unit_number.get_text(strip=True) if unit_number else None

        # -------------------------
        # ATTRIBUTES CELL
        # -------------------------
        attrs = row.select_one("td.plan__attributes")

        beds = attrs.select_one("meta[itemprop='numberOfBedrooms']")
        baths = attrs.select_one("meta[itemprop='numberOfBathroomsTotal']")

        bed = beds["content"] if beds else None
        bath = baths["content"] if baths else None
        floorplan_name = f"{bed}BR/{bath} BA" if bed and bath else None

        sqft_meta = attrs.select_one("meta[itemprop='floorSize']")
        square_feet = int(re.search(r"\d+", sqft_meta["content"]).group()) if sqft_meta else None

        # -------------------------
        # AMENITIES (schema.org)
        # -------------------------
        amenities = [
            m["content"]
            for m in attrs.select("span[itemprop='amenityFeature'] meta[itemprop='name']")
        ]
        amenities = ", ".join(amenities) if amenities else None

        # -------------------------
        # RENT
        # -------------------------
        rent_cell = row.select_one("td.plan__rent")
        rent_match = re.search(r"\$([\d,]+)", rent_cell.get_text())
        starting_rent = int(rent_match.group(1).replace(",", "")) if rent_match else None

        # -------------------------
        # AVAILABILITY
        # -------------------------
        avail_cell = row.select_one("td.plan__availability__date")
        available_date = avail_cell.get_text(strip=True).replace("Available:", "").strip()

        rows.append({
            "unit_number": unit_number,
            "floorplan_name": floorplan_name,
            "available_date": available_date,
            "starting_rent": starting_rent,
            "square_feet": square_feet,
            "building_number": None,
            "amenities": amenities,
            "specials": None
        })

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)