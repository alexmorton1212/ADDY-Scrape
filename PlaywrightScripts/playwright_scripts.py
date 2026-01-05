
import os
import random
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
# NEXT Scripts
# -----------------------------------------------------------------------------------

 