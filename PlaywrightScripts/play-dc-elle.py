
import os
from scripts_playwright import response_script
from scripts_data import data_sightmap

# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

FOLDER_NAME = "Elle"

MAIN_URL = "https://www.elleapartments.com/sightmap/"

MAIN_DIR = "/Users/alexmorton/Desktop/ADDY-Scrape/PlaywrightOutputs"
os.makedirs(MAIN_DIR, exist_ok=True)
HTML_DIR = f"{MAIN_DIR}/HTML/{FOLDER_NAME}"
os.makedirs(HTML_DIR, exist_ok=True)
DATA_DIR = f"{MAIN_DIR}/Data"
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_JSON_FILE = f"{HTML_DIR}/{FOLDER_NAME.lower()}.json"
MAIN_CSV_FILE = f"{DATA_DIR}/{FOLDER_NAME.lower()}.csv"

# -----------------------------------------------------------------------------------
# Response URL Matching
# -----------------------------------------------------------------------------------

def response_criteria(response):
    url = response.url.lower()
    return (
        "sightmap" in url
        and "api" in url
        and "sightmaps" in url
    )

# -----------------------------------------------------------------------------------
# Batch Entrypoint
# -----------------------------------------------------------------------------------

def run():
    response_script(MAIN_URL, MAIN_JSON_FILE, response_criteria)
    data_sightmap(MAIN_JSON_FILE, MAIN_CSV_FILE)

# -----------------------------------------------------------------------------------
# Run Standalone
# -----------------------------------------------------------------------------------

if __name__ == "__main__": run()






# -----------------------------------------------------------------------------------
# Get HTML (Floorplan Details)
# -----------------------------------------------------------------------------------

# has_next = """
# (function () {
#     var next = document.querySelector('li.next a');
#     return !!next;
# })();
# """

# go_next = """
# (function () {
#     var next = document.querySelector('li.next a');
#     if (next) { next.click(); }
# })();
# """

# paginated_navigation_script(MAIN_URL, HTML_DIR, APT_NAME, has_next, go_next)


# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

# rows = []
# pattern = re.compile(rf"^{re.escape(APT_NAME)}_\d+\.html$")

# for filename in os.listdir(HTML_DIR):

#     if not pattern.match(filename): continue
#     path = os.path.join(HTML_DIR, filename)

#     with open(path, "r", encoding="utf-8", errors="ignore") as f:
#         soup = BeautifulSoup(f, "lxml")

#     listings = soup.select("div.fp-listing-item")

#     for item in listings:

#         # unit number
#         unit_number = item.select_one("h3")
#         unit_number = unit_number.get_text(strip=True) if unit_number else None

#         # floorplan name
#         fp_link = item.select_one("a.rfwa-fee-calculator")
#         floorplan_name = fp_link.get("data-fp-name") if fp_link else None

#         # available date
#         available_date = fp_link.get("data-available") if fp_link else None
#         if available_date: available_date = available_date.replace("Available ", "").strip()

#         # base rent
#         base_rent = item.select_one("span.base-rent")
#         base_rent = base_rent.get_text(strip=True) if base_rent else None
#         if base_rent: base_rent = base_rent.replace("base rent", "").strip()

#         # square footage
#         sqft = item.select_one("p[itemprop='floorSize']")
#         sqft = sqft.get_text(strip=True) if sqft else None
#         if sqft: sqft = sqft.replace("SQ FT", "").strip()

#         rows.append({
#             "unit_number": unit_number,
#             "floorplan_name": floorplan_name,
#             "available_date": available_date,
#             "starting_rent": base_rent,
#             "square_feet": sqft,
#             "building_number": None,
#             "amenities": None,
#             "specials": None
#         })

# pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)