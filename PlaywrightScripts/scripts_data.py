
import json
import re
import pandas as pd
from bs4 import BeautifulSoup


# ===========================================================================================================
# Common Data Extraction Scripts
# ===========================================================================================================

# -----------------------------------------------------------------------------------
# Sightmap Data
# -----------------------------------------------------------------------------------

def data_sightmap(json_path, csv_path):

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    units = data["data"]["units"]
    floorplans = data["data"]["floor_plans"]
    floorplan_lookup = {fp["id"]: fp["name"] for fp in floorplans}
    rows = []

    for unit in units:

        floorplan_name = floorplan_lookup.get(unit.get("floor_plan_id"))
        if isinstance(floorplan_name, str) and floorplan_name.startswith("{"):
            floorplan_name = json.loads(floorplan_name).get("name")
    
        rows.append({
            "unit_number": unit.get("unit_number"),
            "floorplan_name": floorplan_name,
            "available_date": unit.get("available_on"),
            "starting_rent": unit.get("price"),
            "square_feet": unit.get("area"),
            "building_number": unit.get("building"),
            "amenities": None,
            "specials": None
        })

    pd.DataFrame(rows).to_csv(csv_path, index=False)


# -----------------------------------------------------------------------------------
# Knock Rentals Data
# -----------------------------------------------------------------------------------

def data_knock(json_path, csv_path):

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    units = data["units_data"]["units"]
    rows = []

    for unit in units:

        if "park" in unit.get("layoutName").lower() or unit.get("area") == 0:
            continue
        
        rows.append({
            "unit_number": unit.get("name"),
            "floorplan_name": unit.get("layoutName"),
            "available_date": unit.get("availableOn"),
            "starting_rent": unit.get("displayPrice"),
            "square_feet": unit.get("area"),
            "building_number": None,
            "amenities": None,
            "specials": None
        })

    pd.DataFrame(rows).to_csv(csv_path, index=False)


# -----------------------------------------------------------------------------------
#  UDR Data
# -----------------------------------------------------------------------------------

def data_udr(html_path, csv_path):

    rows = []

    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    for unit in soup.select("article#unitListingContainer ul#unitResults > li.apartment"):

        # floorplan name
        floorplan = unit.get("data-floor-plan-name")

        # unit number
        unit_number = unit.get("data-number")

        # starting price
        starting_price = int(unit.get("data-base-rent"))

        # sqft
        square_feet = int(unit.get("data-sqft"))

        # availability
        avail_text = unit.select_one(".unit-available-date").get_text(" ", strip=True)
        availability = "Now" if "Now" in avail_text else avail_text.replace("Available Date:", "").strip()

        # amenities
        amenities = ", ".join(
            li.get_text(" ", strip=True)
            for li in unit.select(".amenities-group-section__list > li")
        )

        # specials
        special_items = unit.select(
            ".special-offers ul > li:not(.restrictions-disclaimer)"
        )
        specials = (
            ", ".join(li.get_text(" ", strip=True) for li in special_items)
            if special_items
            else None
        )

        rows.append({
            "unit_number": unit_number,
            "floorplan_name": floorplan,
            "available_date": availability,
            "starting_rent": starting_price,
            "square_feet": square_feet,
            "building_number": None,
            "amenities": amenities,
            "specials": specials
        })    

    pd.DataFrame(rows).to_csv(csv_path, index=False)


# -----------------------------------------------------------------------------------
#  Wydown Data
# -----------------------------------------------------------------------------------

def data_wydown(json_path, csv_path, json_name):

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for unit in data["values"]:

        unit_data = unit["data"]
        property_list = unit["data"]["property_lists"]

        if any(p.get("name") == json_name for p in property_list):

            rows.append({
                "unit_number": unit_data.get("address_address1"),
                "floorplan_name": unit_data.get("marketing_title"),
                "available_date": unit_data.get("available_date"),
                "starting_rent": unit_data.get("market_rent"),
                "square_feet": unit_data.get("square_feet"),
                "building_number": None,
                "amenities": None,
                "specials": None
            })

    pd.DataFrame(rows).to_csv(csv_path, index=False)


# -----------------------------------------------------------------------------------
#  Bradford Data
# -----------------------------------------------------------------------------------

def data_bradford(json_path, csv_path):

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for unit in data:

        keywords = ("waive", "free", "month")
        descr_parts = re.split(r"<br\s*/?>", unit.get("description"), flags=re.IGNORECASE)
        descr_result = next((part.strip() for part in descr_parts if any(k in part.lower() for k in keywords)),None)
        building, unit_part = unit.get("title").split("#", 1)

        rows.append({
            "unit_number": unit_part.strip().split()[0],
            "floorplan_name": unit.get("propertyType"),
            "available_date": unit.get("dateAvailable"),
            "starting_rent": unit.get("rentAmount"),
            "square_feet": unit.get("area"),
            "building_number": building.strip(),
            "amenities": None,
            "specials": descr_result
        })

    pd.DataFrame(rows).to_csv(csv_path, index=False)


# -----------------------------------------------------------------------------------
#  Urby Data
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


# -----------------------------------------------------------------------------------
#  Greystar Data
# -----------------------------------------------------------------------------------

def data_greystar(html_path, csv_path):

    rows = []

    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    next_data = soup.find("script", id="__NEXT_DATA__")
    if not next_data: raise ValueError("__NEXT_DATA__ not found")
    data = json.loads(next_data.string)
    units = data["props"]["pageProps"]["page"]["layout"]["sitecore"]["context"]["property"]["availableUnits"]

    for unit in units:
        rows.append({
            "unit_number": unit.get("unitNumber"),
            "floorplan_name": unit.get("floorPlanLabel"),
            "available_date": unit.get("availableOn"),
            "starting_rent": unit.get("minBasePrice"),
            "square_feet": unit.get("area"),
            "building_number": None,
            "amenities": None,
            "specials": None
        })

    pd.DataFrame(rows).to_csv(csv_path, index=False)


# -----------------------------------------------------------------------------------
#  SecureCafe Data
# -----------------------------------------------------------------------------------

def data_securecafe(html_path, csv_path):

    rows = []

    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    for header in soup.select("div[id^='other-floorplans'] h3"):

        floorplan_name = header.get_text(" ", strip=True)
        floorplan_name = re.sub(r"^Floor Plan\s*:\s*", "", floorplan_name)

        table = header.find_next("table", class_="availableUnits")
        if not table: continue

        for row in table.select("tr.AvailUnitRow"):

            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            unit_number = cells[0].get_text(strip=True).lstrip("#")
            square_feet = int(cells[1].get_text(strip=True))
            rent_text = cells[2].get_text(strip=True)
            rent_first_part = rent_text.split("-")[0]
            starting_rent = int(rent_first_part.replace("$", "").replace(",", ""))

            available_date = None
            btn = row.select_one("input.UnitSelect")
            if btn: 
                m = re.search(r'ApplyNowClick\([^,]+,[^,]+,[^,]+,\s*"([^"]+)"', btn.get("onclick", ""))
                available_date = m.group(1) if m else None

            date_cell = row.select_one("td[data-label='Date Available'] span")
            if date_cell and not btn:
                available_date = date_cell.get_text(strip=True) if date_cell else None

            amenities = None
            amenities_label = row.select(".divUnitInfo ul li label")
            if amenities_label:
                amenities = ", ".join(
                    label.get_text(strip=True)
                    for label in row.select(".divUnitInfo ul li label")
                )

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

    pd.DataFrame(rows).to_csv(csv_path, index=False)


# -----------------------------------------------------------------------------------
#  Pynwheel Data
# -----------------------------------------------------------------------------------

def data_pynwheel(html_path, csv_path):

    rows = []

    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    script = soup.find("script", string=re.compile(r"var\s+available_units\s*="))
    if not script: raise ValueError("available_units variable not found")

    match = re.search(
        r"var\s+available_units\s*=\s*(\[\s*.*?\s*\]);",
        script.string,
        flags=re.DOTALL
    )
    if not match: raise ValueError("Could not extract available_units array")

    units = json.loads(match.group(1))

    for unit in units: 

        rows.append({
            "unit_number": unit.get("UnitCode"),
            "floorplan_name": unit.get("FloorPlanName"),
            "available_date": unit.get("AvailableDate"),
            "starting_rent": unit.get("IpmDisplayMinRent"),
            "square_feet": unit.get("SquareFeet"),
            "building_number": None,
            "amenities": None,
            "specials": None
        })

    pd.DataFrame(rows).to_csv(csv_path, index=False)



# ===========================================================================================================
# Unique Data Extraction Scripts
# ===========================================================================================================

# -----------------------------------------------------------------------------------
#  West End 25 Data
# -----------------------------------------------------------------------------------

def data_westend25(html_path, csv_path):

    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    units_js = next(
        s.string for s in soup.find_all("script")
        if s.string and "var unitsData" in s.string
    )

    units_js = (
        units_js
        .replace("var unitsData =", "")
        .strip()
        .rstrip(";")
        .strip("'")
        .encode("utf-8")
        .decode("unicode_escape")
    )

    units_data = json.loads(units_js)

    rows = [
        {
            "unit_number": u.get("unit_number"),
            "floorplan_name": u.get("floorplan_name"),
            "available_date": u.get("available_on"),
            "starting_rent": u.get("min_rent"),
            "square_feet": u.get("sqft_unit") or u.get("sqft"),
            "building_number": None,
            "amenities": None,
            "specials": None
        }
        for units in units_data.values()
        for u in units
    ]

    pd.DataFrame(rows).to_csv(csv_path, index=False)