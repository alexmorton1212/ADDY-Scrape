
### Script for Landing Page / Exploration

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