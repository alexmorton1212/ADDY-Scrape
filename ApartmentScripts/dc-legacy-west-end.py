
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


# ===============================================================
# Configuration
# ===============================================================

TODAYS_DATE = "2025-TODAY"

APT_NAME = "legacywestend"
FOLDER_NAME = "LegacyWestEnd"

BASE_URL = "https://legacydcapartments.com"
MAIN_URL = "https://legacydcapartments.com/floor-plans/"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
SUB_HTML_FILE = OUTPUT_DIR + APT_NAME + "_sub.html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Helper Functions
# ===============================================================

def run_script(url, output_file):

    return f'''

    tell application "Google Chrome"
        activate
        open location "{url}"
    end tell

    delay 7

    tell application "Google Chrome"
        set html to execute front window's active tab javascript "
            document.documentElement.outerHTML
        "
        close active tab of front window
    end tell

    set f to open for access POSIX file "{output_file}" with write permission
    write html to f
    close access f
    '''

# ===============================================================
# Get HTML (Main)
# ===============================================================

main_script = run_script(MAIN_URL, MAIN_HTML_FILE)
subprocess.run(["osascript", "-e", main_script])


# ===============================================================
# Get URL (Floorplan Details)
# ===============================================================

with open(MAIN_HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
    soup = BeautifulSoup(f, "lxml")

iframe = soup.find("iframe", title="Floor Plans")
if iframe and iframe.get("src"): iframe_url = iframe["src"]
else: raise ValueError("Floor Plans iframe not found")


# ===============================================================
# Get HTML (Floorplan Details)
# ===============================================================

sub_script = run_script(iframe_url, SUB_HTML_FILE)
subprocess.run(["osascript", "-e", sub_script])


# ===============================================================
# Get Target Modals (Floorplan Details)
# ===============================================================

with open(SUB_HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
    soup = BeautifulSoup(f, "lxml")

click_ids = []

for block in soup.select("div.fplist"):
    avail_span = block.select_one("span[id*='List1AvailUnits']")
    link = block.select_one("a[id]")
    if not avail_span or not link: continue
    if avail_span.get_text(strip=True) == "0": continue
    click_ids.append(link["id"])


# ===============================================================
# Create Script (Floorplan Details)
# ===============================================================

def build_simple_click_script(url, click_ids, output_dir, initial_delay=7, click_delay=5):

    blocks = []

    for i, click_id in enumerate(click_ids, start=1):
        
        blocks.append(f'''
        -- click {click_id}
        tell application "Google Chrome"
            tell front window's active tab
                execute javascript "
                    var link = document.getElementById('{click_id}');
                    if (link) {{
                        link.click();
                    }} else {{
                        console.log('Link not found: {click_id}');
                    }}
                "
            end tell
        end tell

        delay {click_delay}

        tell application "Google Chrome"
            set html to execute front window's active tab javascript "
                document.documentElement.outerHTML
            "
        end tell

        set f to open for access POSIX file "{output_dir}{APT_NAME}_{i}.html" with write permission
        write html to f
        close access f

        -- go back to list page
        tell application "Google Chrome"
            tell front window's active tab
                execute javascript "history.back();"
            end tell
        end tell

        delay {click_delay}

        ''')

    return f'''
    tell application "Google Chrome"
        activate
        open location "{url}"
    end tell

    delay {initial_delay}

    {''.join(blocks)}
    '''

result = build_simple_click_script(iframe_url, click_ids, OUTPUT_DIR)
subprocess.run(["osascript", "-e", result])


# ===============================================================
# Get Data (Floorplan Details)
# ===============================================================

rows = []
pattern = re.compile(r"^legacywestend_\d+\.html$")

for filename in os.listdir(OUTPUT_DIR):

    if not pattern.match(filename): continue
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    fp_name = soup.select_one("#ctl00_main_FullFPDescr")
    fp_info = soup.select_one("#ctl00_main_FullFPInfo")
    bldg_span = soup.select_one("span[id*='UnitRMBLDGID']")
    
    building_number = bldg_span.get_text(strip=True) if bldg_span else None
    floorplan_name = fp_name.get_text(strip=True) if fp_name else None

    square_feet = None
    if fp_info:
        parts = fp_info.get_text(" ", strip=True).split("|")
        for p in parts:
            if "sq" in p:
                square_feet = p.replace("sq.", "").replace("ft.", "").strip()

    for tr in soup.select("#ctl00_main_UnitGrid tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue

        rows.append({
            "unit_number": tds[1].get_text(strip=True),
            "floorplan_name": floorplan_name,
            "available_date": tds[2].get_text(strip=True),
            "starting_rent": tds[3].get_text(strip=True).strip('"'),
            "square_feet": square_feet,
            "building_number": building_number
        })

pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)