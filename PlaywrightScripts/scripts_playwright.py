
# ===================================================================================
# PLAYWRIGHT: HTML EXTRACTION SCRIPTS
# ===================================================================================

import os
import json
import random
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from config import CHANNEL, USER_AGENT, VIEWPORT, HEADLESS


# -----------------------------------------------------------------------------------
# Single Page Script
# -----------------------------------------------------------------------------------

def single_page_script(url, html_output):

    with sync_playwright() as p:

        browser = p.chromium.launch(channel=CHANNEL, headless=HEADLESS)
        context = browser.new_context(user_agent=USER_AGENT,viewport=VIEWPORT)

        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        html = page.content()

        with open(html_output, "w", encoding="utf-8") as f:
            f.write(html)

        page.close()
        context.close()
        browser.close()


def single_page_scroll_script(url, html_output):

    with sync_playwright() as p:
        browser = p.chromium.launch(channel=CHANNEL, headless=HEADLESS)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport=VIEWPORT
        )

        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")

        # scroll to bottom to trigger lazy-loaded content
        page.evaluate("""
            () => {
                window.scrollTo(0, document.body.scrollHeight);
            }
        """)

        # give JS time to inject content
        page.wait_for_timeout(3000)

        html = page.content()

        with open(html_output, "w", encoding="utf-8") as f:
            f.write(html)

        page.close()
        context.close()
        browser.close()


# -----------------------------------------------------------------------------------
# Pagination Scripts
# -----------------------------------------------------------------------------------

def paginated_navigation_script(url, output_dir, base_name, has_next, go_next):

    with sync_playwright() as p:

        browser = p.chromium.launch(channel=CHANNEL, headless=HEADLESS)
        context = browser.new_context(user_agent=USER_AGENT,viewport=VIEWPORT)

        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page_num = 1

        while True:
            
            html = page.content()
            file_path = os.path.join(output_dir, f"{base_name}_{page_num}.html")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)

            has_next_result = page.evaluate(has_next)
            if not has_next_result:
                break

            with page.expect_navigation(wait_until="domcontentloaded"):
                page.evaluate(go_next)
            
            page_num += 1
            page.wait_for_timeout(random.randint(400, 1200))

        page.close()
        context.close()
        browser.close()


def paginated_inplace_script(url, output_dir, base_name, has_next, go_next, change_signal):

    with sync_playwright() as p:

        browser = p.chromium.launch(channel=CHANNEL, headless=HEADLESS)
        context = browser.new_context(user_agent=USER_AGENT,viewport=VIEWPORT)

        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page_num = 1

        while True:
            
            html = page.content()
            file_path = os.path.join(output_dir, f"{base_name}_{page_num}.html")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)

            has_next_result = page.evaluate(has_next)
            if not has_next_result:
                break

            prev_state = page.evaluate(change_signal)
            page.evaluate(go_next)
            page.wait_for_function(
                """
                ([prev, signal]) => {
                    try {
                        const current = eval(signal);
                        return current !== prev;
                    } catch {
                        return false;
                    }
                }
                """,
                arg=[prev_state, change_signal],
                timeout=15000
            )

            page_num += 1
            page.wait_for_timeout(random.randint(400, 1200))

        page.close()
        context.close()
        browser.close()


# -----------------------------------------------------------------------------------
# Response Script
# -----------------------------------------------------------------------------------

def response_script(url, output_file, response_matcher):

    with sync_playwright() as p:

        browser = p.chromium.launch(channel=CHANNEL, headless=HEADLESS)
        context = browser.new_context(user_agent=USER_AGENT, viewport=VIEWPORT)
        page = context.new_page()
        captured = False

        def handle_response(response):

            nonlocal captured
            
            try:
                if not captured and response_matcher(response):
                    data = response.json()
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    captured = True

            except Exception: pass

        page.on("response", handle_response)
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(6000)
        if not captured:
            page.wait_for_timeout(6000)
            if not captured:
                page.wait_for_timeout(6000)
                
        page.close()
        context.close()
        browser.close()


# -----------------------------------------------------------------------------------
# SecureCafe Scripts
# -----------------------------------------------------------------------------------

### TODO: Turn on headless

def securecafe_script(url, html_output):
    
    with sync_playwright() as p:

        browser = p.chromium.launch(channel=CHANNEL, headless=False)
        context = browser.new_context(user_agent=USER_AGENT, viewport=VIEWPORT)
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded")

        # Ensure button is real & clickable
        page.wait_for_selector("button.btn-viewDetails", state="visible")
        btn = page.locator("button.btn-viewDetails").first
        btn.scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        # Force click (SecureCafe requires this)
        btn.click(force=True)

        # Wait for AJAX to finish
        page.wait_for_load_state("networkidle")

        # Capture LIVE DOM (not cached)
        html = page.evaluate("document.documentElement.outerHTML")

        with open("wren_5.html", "w", encoding="utf-8") as f:
            f.write(html)

        page.close()
        context.close()
        browser.close()


def capture_floorplan_pages(url, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel=CHANNEL, headless=False)
        context = browser.new_context(user_agent=USER_AGENT, viewport=VIEWPORT)
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded")

        links = page.locator("a.floorplan-action-button[name='applynow']")
        count = links.count()

        base_url = page.url

        for i in range(5):
            href = links.nth(i).get_attribute("href")
            target_url = urljoin(base_url, href)

            page.goto(target_url, wait_until="domcontentloaded")

            html = page.content()
            with open(f"{output_dir}/floorplan_{i}.html", "w", encoding="utf-8") as f:
                f.write(html)

            page.goto(url, wait_until="domcontentloaded")

        page.close()
        context.close()
        browser.close()
