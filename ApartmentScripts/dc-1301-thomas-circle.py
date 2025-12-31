
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

APT_NAME = "1301thomascircle"
FOLDER_NAME = "1301ThomasCircle"

BASE_URL = "https://www.udr.com/washington-dc-apartments/logan-circle/1301-thomas-circle"
MAIN_URL = "https://www.udr.com/washington-dc-apartments/logan-circle/1301-thomas-circle/apartments-pricing/"

OUTPUT_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/" + TODAYS_DATE + "/" + FOLDER_NAME + "/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAIN_HTML_FILE = OUTPUT_DIR + APT_NAME + ".html"
MAIN_CSV_FILE = OUTPUT_DIR + APT_NAME + ".csv"


# ===============================================================
# Get HTML (Main)
# ===============================================================

main_script = landing_script(MAIN_URL, MAIN_HTML_FILE)
subprocess.run(["osascript", "-e", main_script])
