
# ===================================================================================
# COMMON DATA EXTRACTION SCRIPTS
# ===================================================================================

import json
import pandas as pd
from bs4 import BeautifulSoup

# -----------------------------------------------------------------------------------
# Gables Data
# -----------------------------------------------------------------------------------

def data_gables(json_path, csv_path):

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    units = data["units_data"]["units"]

    rows = []
    for unit in units:
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
#  UDR Data
# -----------------------------------------------------------------------------------

### 1301 Thomas Circle, Andover House

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

### The Heywood

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

