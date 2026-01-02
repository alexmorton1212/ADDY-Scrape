

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

APT_NAME = "balsa"
FOLDER_NAME = "Balsa"

BASE_URL = "https://livebalsa.com"
MAIN_URL = "https://livebalsa.com/floorplans/"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Helper Functions
# ===============================================================

def get_engrain_floor_labels(url):

    return f'''

    tell application "Google Chrome"
        activate
        open location "{url}"
    end tell

    delay 7

    tell application "Google Chrome"
        set floorLabels to execute front window's active tab javascript "
            Array.from(
              document.querySelectorAll('[data-jd-fp-selector=\\\"map-embed-floor\\\"]')
            )
            .filter(el => {{
                const span = el.querySelector(
                  '[data-jd-fp-selector=\\\"map-embed-floor-avail-count\\\"]'
                );
                if (!span) return false;
                const val = span.textContent.trim();
                return val !== '--' && !isNaN(val) && Number(val) > 0;
            }})
            .map(el => el.getAttribute('aria-label'))
            .join(',');
        "
    end tell

    return floorLabels

    '''

def generate_engrain_floor_click_script(output_dir, floor_labels):

    blocks = []

    for label in floor_labels:
        floor_num = label.replace("Floor ", "").strip()

        blocks.append(f'''

        delay 0.5

        -- Click {label}
        tell application "Google Chrome"
            tell front window's active tab
                execute javascript "
                    document.querySelector(
                      'a[aria-label=\\\"{label}\\\"]'
                    )?.click();
                "
            end tell
        end tell

        delay 1

        tell application "Google Chrome"
            set html to execute front window's active tab javascript "
                document.documentElement.outerHTML
            "
        end tell

        set f to open for access POSIX file "{output_dir}/{APT_NAME}_{floor_num}.html" with write permission
        write html to f
        close access f

        ''')

    blocks_text = "\n".join(blocks)

    return f'''

    tell application "Google Chrome"
        activate
    end tell

    delay 2

    {blocks_text}

    tell application "Google Chrome"
        close active tab of front window
    end tell

    '''


# ===============================================================
# Get Floors Available
# ===============================================================

floor_script = get_engrain_floor_labels(MAIN_URL)
result = subprocess.run(["osascript", "-e", floor_script], capture_output=True, text=True)
floor_labels = result.stdout.strip().split(",")


# ===============================================================
# Get HTML (Floorplan Details)
# ===============================================================

big_script = generate_engrain_floor_click_script(OUTPUT_DIR, floor_labels)
subprocess.run(["osascript", "-e", big_script], capture_output=True, text=True)


# ===============================================================
# Get Data (Floorplan Details)
# ===============================================================

rows = []
pattern = re.compile(r"^balsa_")

for filename in os.listdir(OUTPUT_DIR):

    if not pattern.match(filename): continue
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    for card in soup.select('a[data-jd-fp-selector="unit-card"]'):

        # FLOORPLAN
        floorplan = card.select_one(".jd-fp-unit-card__floorplan-title span").get_text(strip=True)

        # UNIT NUMBER
        unit = card.select_one(".jd-fp-card-info__title--large").get_text(strip=True).replace("#", "")

        # AVAILABILITY
        avail_raw = card.select_one(".jd-fp-card-info__text--brand").get_text(strip=True)
        availability = ("Now" if "Now" in avail_raw else avail_raw.replace("Available ", ""))

        # STARTING PRICE
        price_text = card.select_one(".jd-fp-strong-text").get_text()
        price = int(re.search(r"\$([\d,]+)", price_text).group(1).replace(",", ""))

        # SQFT
        details = card.select_one("p.jd-fp-card-info__text").get_text(" ", strip=True)
        sqft = int(re.search(r"(\d+)\s*sq", details, re.I).group(1))

        rows.append({
            "unit_number": unit,
            "floorplan_name": floorplan,
            "available_date": availability,
            "starting_rent": price,
            "square_feet": sqft,
            "building_number": None,
            "amenities": None,
            "specials": None
        })    

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)
