"""Background-friendly login: opens a visible Chromium window and waits for the URL
to settle on the real Ross Recruit site (i.e. you've finished signing in + Okta Verify)
instead of requiring an Enter keypress in a terminal. Meant to be launched by
watch_and_renew.sh, not run directly (though `python auto_login.py <url>` still works).
"""
import sys, time
from playwright.sync_api import sync_playwright

START = sys.argv[1] if len(sys.argv) > 1 else "https://michiganross.12twenty.com/events"
LOGGED_IN_HOST = "michiganross.12twenty.com"
LOGGED_OUT_MARKERS = ("okta", "sso.12twenty.com", "shibboleth", "/login")
TIMEOUT_S = 600  # give up after 10 minutes of nobody logging in

with sync_playwright() as p:
    b = p.chromium.launch(headless=False)
    ctx = b.new_context()
    page = ctx.new_page()
    page.goto(START)
    deadline = time.time() + TIMEOUT_S
    settled = False
    while time.time() < deadline:
        url = page.url.lower()
        if LOGGED_IN_HOST in url and not any(m in url for m in LOGGED_OUT_MARKERS):
            # give the SPA a moment to finish its post-login API calls before saving
            page.wait_for_timeout(3000)
            settled = True
            break
        time.sleep(2)
    if not settled:
        print("TIMEOUT: nobody completed the login within the time limit.")
        b.close()
        sys.exit(1)
    ctx.storage_state(path="storage_state.json")
    b.close()
print("OK: storage_state.json saved.")
