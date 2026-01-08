
import os
from scripts_playwright import response_script
from scripts_data import data_sightmap


# -----------------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------------

APT_NAME = "margarite"
FOLDER_NAME = "Margarite"

BASE_URL = "https://margaritedc.com"
MAIN_URL = "https://margaritedc.com/sightmap/"

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
# Get HTML (Main)
# -----------------------------------------------------------------------------------

def response_criteria(response):
    url = response.url.lower()
    return (
        "sightmap" in url
        and "api" in url
        and "sightmaps" in url
    )

response_script(MAIN_URL, MAIN_JSON_FILE, response_criteria)


# -----------------------------------------------------------------------------------
# Get Data (Floorplan Details)
# -----------------------------------------------------------------------------------

data_sightmap(MAIN_JSON_FILE, MAIN_CSV_FILE)



# -----------------------------------------------------------------------------------
# Get HTML (Floorplan Details)
# -----------------------------------------------------------------------------------

# has_next = """
# (function () {
#     var nextBtn = document.querySelector('#neodtable_next');
#     return nextBtn && !nextBtn.classList.contains('disabled');
# })();
# """

# go_next = """
# (function () {
#     var nextBtn = document.querySelector('#neodtable_next');
#     if (nextBtn && !nextBtn.classList.contains('disabled')) { nextBtn.click(); }
# })();
# """

# change_signal = """
# (function () {
#     var current = document.querySelector('.paginate_button.current');
#     return current ? current.getAttribute('data-dt-idx') : '';
# })();
# """

# paginated_inplace_script(MAIN_URL, HTML_DIR, APT_NAME, has_next, go_next, change_signal)


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

#     listings = soup.select("table#neodtable tbody.plan__cards > tr.plan__card")

#     for row in listings:

#         # unit number
#         unit_number = row.select_one("td.plan__name h5")
#         unit_number = unit_number.get_text(strip=True) if unit_number else None

#         # floorplan name
#         attrs = row.select_one("td.plan__attributes")
#         beds = attrs.select_one("meta[itemprop='numberOfBedrooms']")
#         baths = attrs.select_one("meta[itemprop='numberOfBathroomsTotal']")
#         bed = beds["content"] if beds else None
#         bath = baths["content"] if baths else None
#         floorplan_name = f"{bed}BR/{bath} BA" if bed and bath else None

#         # square feet
#         sqft_meta = attrs.select_one("meta[itemprop='floorSize']")
#         square_feet = int(re.search(r"\d+", sqft_meta["content"]).group()) if sqft_meta else None

#         # amenities
#         amenities = [
#             m["content"]
#             for m in attrs.select("span[itemprop='amenityFeature'] meta[itemprop='name']")
#         ]
#         amenities = ", ".join(amenities) if amenities else None

#         # starting rent
#         rent_cell = row.select_one("td.plan__rent")
#         rent_match = re.search(r"\$([\d,]+)", rent_cell.get_text())
#         starting_rent = int(rent_match.group(1).replace(",", "")) if rent_match else None

#         # availability
#         avail_cell = row.select_one("td.plan__availability__date")
#         available_date = avail_cell.get_text(strip=True).replace("Available:", "").strip()

#         rows.append({
#             "unit_number": unit_number,
#             "floorplan_name": floorplan_name,
#             "available_date": available_date,
#             "starting_rent": starting_rent,
#             "square_feet": square_feet,
#             "building_number": None,
#             "amenities": amenities,
#             "specials": None
#         })

# pd.DataFrame(rows).to_csv(MAIN_CSV_FILE, index=False)