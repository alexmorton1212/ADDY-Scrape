import os
import pandas as pd
from bs4 import BeautifulSoup

### Script for Single Page / Exploration

def landing_script(url, output_file):

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


### Scripts for Gables owned websites

def gables_script(url, output_dir, base_name):

    return f'''
    set pageNum to 1
    set modalNum to 1

    tell application "Google Chrome"
        activate
        open location "{url}"
    end tell

    delay 7

    repeat
        -- how many Available Home(s) buttons on this page?
        tell application "Google Chrome"
            set btnCount to execute front window's active tab javascript "
                Array.from(document.querySelectorAll('button'))
                    .filter(b => b.innerText && b.innerText.includes('Available Home'))
                    .length;
            "
        end tell

        repeat with i from 1 to btnCount
            -- open i-th Available Home
            tell application "Google Chrome"
                execute front window's active tab javascript "
                    var btn = Array.from(document.querySelectorAll('button'))
                        .filter(b => b.innerText && b.innerText.includes('Available Home'))[" & (i - 1) & "];
                    if (btn) btn.click();
                "
            end tell

            delay 1

            -- SAVE FULL PAGE HTML (modal open)
            tell application "Google Chrome"
                set html to execute front window's active tab javascript "
                    document.documentElement.outerHTML;
                "
            end tell

            set filePath to "{output_dir}" & "{base_name}_" & pageNum & "_" & modalNum & ".html"
            set f to open for access POSIX file filePath with write permission
            write html to f
            close access f

            set modalNum to modalNum + 1

            -- close modal via keyboard
            tell application "System Events"
                keystroke tab
                delay 0.3
                keystroke return
            end tell

            delay 1

        end repeat

        -- check if Next exists
        tell application "Google Chrome"
            set hasNext to execute front window's active tab javascript "
                var b = Array.from(document.querySelectorAll('button'))
                    .find(x => x.innerText && x.innerText.trim() === 'Next');
                (b && !b.disabled) ? 'YES' : 'NO';
            "
        end tell

        if hasNext is "NO" then exit repeat

        -- go to next page
        tell application "Google Chrome"
            execute front window's active tab javascript "
                var b = Array.from(document.querySelectorAll('button'))
                    .find(x => x.innerText && x.innerText.trim() === 'Next');
                if (b) b.click();
            "
        end tell

        set pageNum to pageNum + 1

        delay 2

    end repeat

    tell application "Google Chrome"
        close active tab of front window
    end tell
    '''

def gables_get_data(output_dir, csv, pattern):

    rows = []

    for filename in os.listdir(output_dir):

        if not pattern.match(filename): continue
        path = os.path.join(output_dir, filename)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "lxml")

        # unit type
        unit_type_el = soup.select_one('h3[data-testid$="t-floorplanName"]')
        unit_type = unit_type_el.get_text(strip=True) if unit_type_el else None

        # square footage
        sqft_el = soup.select_one('span[data-testid$="t-minimumSQFT"]')
        sqft = (
            sqft_el.get_text(strip=True)
            .replace("Sq. Ft", "")
            .strip()
            if sqft_el else None
        )

        # available homes table
        table = soup.select_one('table[data-testid$="availableHomes-table"]')
        if not table: continue

        for tr in table.select("tbody tr"):
            tds = tr.find_all("td")
            if len(tds) < 4: continue

            price_text = tds[1].get_text(strip=True)

            spans = tds[3].find_all("span")
            if spans:
                avail_text = spans[-1].get_text(strip=True)
                if avail_text == "Available Now": availability = "Now"
                elif avail_text.startswith("Available ("): availability = avail_text.replace("Available (", "").replace(")", "")
                else: availability = avail_text
            else: availability = None

            rows.append({
                "unit_number": tds[0].get_text(strip=True),
                "floorplan_name": unit_type,
                "available_date": availability,
                "starting_rent": price_text.split("-")[0].strip(),
                "square_feet": sqft,
                "building_number": None,
                "amenities": tds[2].get_text(strip=True),
                "specials": None
            })    

    pd.DataFrame(rows).to_csv(csv, index=False)


### Scripts for UDR owned websites

def udr_get_data(html, csv):

    rows = []

    with open(html, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    for unit in soup.select("article#unitListingContainer ul#unitResults > li.apartment"):

        # FLOORPLAN
        floorplan = unit.get("data-floor-plan-name")

        # UNIT NUMBER
        unit_number = unit.get("data-number")

        # STARTING PRICE
        starting_price = int(unit.get("data-base-rent"))

        # SQFT
        square_feet = int(unit.get("data-sqft"))

        # AVAILABILITY (explicitly use the field that says "Now")
        avail_text = unit.select_one(".unit-available-date").get_text(" ", strip=True)
        availability = "Now" if "Now" in avail_text else avail_text.replace("Available Date:", "").strip()

        # AMENITIES (comma-separated string)
        amenities = ", ".join(
            li.get_text(" ", strip=True)
            for li in unit.select(".amenities-group-section__list > li")
        )

        # SPECIALS (unit-level)
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

    pd.DataFrame(rows).to_csv(csv, index=False)


### Scripts for Sightmap websites

def sightmap_script(url, output_dir, apt_name):

    return f'''
    tell application "Google Chrome"
        activate
        open location "{url}"
    end tell

    delay 7

    -- count floors with availability
    tell application "Google Chrome"
        set floorCount to execute front window's active tab javascript "
            Array.from(document.querySelectorAll('#floor-horizontal-select li'))
                .filter(function(li) {{
                    var label = li.getAttribute('aria-label') || '';
                    return label.indexOf('. 0 APT') === -1;
                }}).length;
        "
    end tell

    repeat with i from 0 to (floorCount - 1)

        -- click floor
        tell application "Google Chrome"
            execute front window's active tab javascript "
                Array.from(document.querySelectorAll('#floor-horizontal-select li'))
                    .filter(function(li) {{
                        var label = li.getAttribute('aria-label') || '';
                        return label.indexOf('. 0 APT') === -1;
                    }})[" & i & "].click();
            "
        end tell

        delay 1

        -- grab HTML
        tell application "Google Chrome"
            set html to execute front window's active tab javascript "
                document.documentElement.outerHTML
            "
        end tell

        -- save file
        set filePath to "{output_dir}/{apt_name}_" & i & ".html"
        set f to open for access POSIX file filePath with write permission
        write html to f
        close access f

        delay 1

    end repeat

    tell application "Google Chrome"
        close active tab of front window
    end tell
    '''


### Original Sightmap Script

def og_sightmap_script(url, output_dir, apt_name):

    return f'''
    tell application "Google Chrome"
        activate
        open location "{url}"
    end tell

    delay 7

    -- count floors with availability
    tell application "Google Chrome"
        set floorCount to execute front window's active tab javascript "
            Array.from(document.querySelectorAll('#floor-horizontal-select li'))
                .filter(function(li) {{
                    var label = li.getAttribute('aria-label') || '';
                    return label.indexOf('0 APT') === -1;
                }}).length;
        "
    end tell

    repeat with i from 0 to (floorCount - 1)

        -- click floor
        tell application "Google Chrome"
            execute front window's active tab javascript "
                Array.from(document.querySelectorAll('#floor-horizontal-select li'))
                    .filter(function(li) {{
                        var label = li.getAttribute('aria-label') || '';
                        return label.indexOf('0 APT') === -1;
                    }})[" & i & "].click();
            "
        end tell

        delay 1

        -- grab HTML
        tell application "Google Chrome"
            set html to execute front window's active tab javascript "
                document.documentElement.outerHTML
            "
        end tell

        -- save file
        set filePath to "{output_dir}/{apt_name}_" & i & ".html"
        set f to open for access POSIX file filePath with write permission
        write html to f
        close access f

        delay 1

    end repeat

    tell application "Google Chrome"
        close active tab of front window
    end tell
    '''