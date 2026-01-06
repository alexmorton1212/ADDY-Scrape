
import os
import json
import pandas as pd
from scripts_playwright import response_script


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "urbynavyyard"
FOLDER_NAME = "UrbyNavyYard"

BASE_URL = "https://www.urby.com/location/washington-dc"
MAIN_URL = "https://www.urby.com/location/washington-dc/availability"

MAIN_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/PlaywrightOutputs"
os.makedirs(MAIN_DIR, exist_ok=True)

HTML_DIR = f"{MAIN_DIR}/HTML/{FOLDER_NAME}"
os.makedirs(HTML_DIR, exist_ok=True)

DATA_DIR = f"{MAIN_DIR}/Data"
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_JSON_FILE = f"{HTML_DIR}/{APT_NAME}.json"
MAIN_CSV_FILE = f"{DATA_DIR}/{APT_NAME}.csv"

# -----------------------------------------------------------------------------------
# Get HTML (Main)
# -----------------------------------------------------------------------------------

def response_criteria(response):
    url = response.url.lower()
    return (
        "getfilteredunitsbycity" in url
        and "city=washington-dc" in url
    )

response_script(MAIN_URL, MAIN_JSON_FILE, response_criteria)

# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

def data_urby(json_path, csv_path):

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    units = data["units"]
    rows = []

    for unit in units:
        rows.append({
            "unit_number": unit.get("unitNumber"),
            "floorplan_name": unit.get("floorplanName"),
            "available_date": unit["unitSpaces"]["unitSpace"][0].get("availableDate"),
            "starting_rent": unit["unitSpaces"]["unitSpace"][0].get("effectiveRent"),
            "square_feet": unit.get("SquareFeet"),
            "building_number": None,
            "amenities": None,
            "specials": None
        })

    pd.DataFrame(rows).to_csv(csv_path, index=False)

data_urby(MAIN_JSON_FILE, MAIN_CSV_FILE)
