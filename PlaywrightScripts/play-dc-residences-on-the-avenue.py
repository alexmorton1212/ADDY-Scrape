
import os
from scripts_playwright import response_script, single_page_script
from scripts_data import data_sightmap

import json
import re
import pandas as pd
from bs4 import BeautifulSoup

# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "residencesontheavenue"
FOLDER_NAME = "ResidencesOnTheAvenue"

BASE_URL = "https://www.residencesontheavenue.com/"
MAIN_URL = "https://www.residencesontheavenue.com/floorplans?Beds=6" # gets json and html at same time

MAIN_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/PlaywrightOutputs"
os.makedirs(MAIN_DIR, exist_ok=True)

HTML_DIR = f"{MAIN_DIR}/HTML/{FOLDER_NAME}"
os.makedirs(HTML_DIR, exist_ok=True)

DATA_DIR = f"{MAIN_DIR}/Data"
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_JSON_FILE = f"{HTML_DIR}/{APT_NAME}.json"
MAIN_HTML_FILE = f"{HTML_DIR}/{APT_NAME}.html"
MAIN_CSV_FILE = f"{DATA_DIR}/{APT_NAME}.csv"


# -----------------------------------------------------------------------------------
# Get JSON (Main)
# -----------------------------------------------------------------------------------

def response_criteria(response):
    url = response.url.lower()
    return (
        "sightmap" in url
        and "api" in url
        and "sightmaps" in url
    )

# response_script(MAIN_URL, MAIN_JSON_FILE, response_criteria)


# -----------------------------------------------------------------------------------
# Get HTML (Main)
# -----------------------------------------------------------------------------------

single_page_script(MAIN_URL, MAIN_HTML_FILE)


def data_residences_townhome(html_path, csv_path):

    rows = []

    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

data_residences_townhome(MAIN_HTML_FILE, MAIN_CSV_FILE)



# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

# data_sightmap(MAIN_JSON_FILE, MAIN_CSV_FILE)