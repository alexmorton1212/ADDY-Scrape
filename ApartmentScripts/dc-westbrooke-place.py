
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
from reusablescripts import gables_script, gables_get_data

# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "westbrookeplace"
FOLDER_NAME = "WestbrookePlace"

BASE_URL = "https://www.gables.com/westbrookeplace"
MAIN_URL = "https://www.gables.com/westbrookeplace#floor-plans"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + "_next.html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Get HTML (Floorplan Details)
# ===============================================================

main_script = gables_script(MAIN_URL, OUTPUT_DIR, APT_NAME)
subprocess.run(["osascript", "-e", main_script])


# ===============================================================
# Get Data (Floorplan Details)
# ===============================================================

pattern = re.compile(r"^westbrookeplace_\d+_\d+\.html$")
gables_get_data(OUTPUT_DIR, MAIN_CSV_FILE, pattern)


# rows = []
# pattern = re.compile(r"^westbrookeplace_\d+_\d+\.html$")

# for filename in os.listdir(OUTPUT_DIR):

#     if not pattern.match(filename): continue
#     path = os.path.join(OUTPUT_DIR, filename)

#     with open(path, "r", encoding="utf-8", errors="ignore") as f:
#         soup = BeautifulSoup(f, "lxml")

#     # unit type
#     unit_type_el = soup.select_one('h3[data-testid$="t-floorplanName"]')
#     unit_type = unit_type_el.get_text(strip=True) if unit_type_el else None

#     # square footage
#     sqft_el = soup.select_one('span[data-testid$="t-minimumSQFT"]')
#     sqft = (
#         sqft_el.get_text(strip=True)
#         .replace("Sq. Ft", "")
#         .strip()
#         if sqft_el else None
#     )

#     # available homes table
#     table = soup.select_one('table[data-testid$="availableHomes-table"]')
#     if not table: continue

#     for tr in table.select("tbody tr"):
#         tds = tr.find_all("td")
#         if len(tds) < 4: continue

#         price_text = tds[1].get_text(strip=True)
#         min_price = price_text.split("-")[0].strip()

#         spans = tds[3].find_all("span")
#         if spans:
#             avail_text = spans[-1].get_text(strip=True)
#             if avail_text == "Available Now": availability = "Now"
#             elif avail_text.startswith("Available ("): availability = avail_text.replace("Available (", "").replace(")", "")
#             else: availability = avail_text
#         else: availability = None

#         rows.append({
#             "unit_number": tds[0].get_text(strip=True),
#             "floorplan_name": unit_type,
#             "available_date": availability,
#             "starting_rent": price_text.split("-")[0].strip(),
#             "square_feet": sqft,
#             "building_number": None,
#             "amenities": tds[2].get_text(strip=True),
#             "specials": None
#         })    

# pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)