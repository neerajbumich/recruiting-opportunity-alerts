"""Background-friendly login: opens a visible Chromium window and polls the browser's
own cookie jar for the real auth cookie instead of watching page navigation (which
proved unreliable to observe from a backgrounded Python process in this environment).
Meant to be launched by watch_and_renew.sh, not run directly (though
`python auto_login.py <url>` still works).
"""
import sys, time
from playwright.sync_api import sync_playwright

START = sys.argv[1] if len(sys.argv) > 1 else "https://michiganross.12twenty.com/events"
AUTH_COOKIE = ".ASPXAUTH.Shared"
AUTH_DOMAIN = "michiganross.12twenty.com"
TIMEOUT_S = 600  # give up after 10 minutes of nobody logging in

with sync_playwright() as p:
    b = p.chromium.launch(headless=False)
    ctx = b.new_context()
    ctx.new_page().goto(START)
    deadline = time.time() + TIMEOUT_S
    settled = False
    last_count = None
    while time.time() < deadline:
        cookies = ctx.cookies()
        if len(cookies) != last_count:
            print(f"DEBUG {len(cookies)} cookies present", flush=True)
            last_count = len(cookies)
        auth = next((c for c in cookies if c["name"] == AUTH_COOKIE and AUTH_DOMAIN in c["domain"]), None)
        if auth and auth.get("value"):
            print(f"DEBUG found {AUTH_COOKIE}, expires={auth.get('expires')}", flush=True)
            time.sleep(2)  # let any last API calls finish
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
