"""Dump a logged-in page's HTML plus any JSON API responses it loads (12Twenty is an SPA)."""
import json, sys
from playwright.sync_api import sync_playwright
calls = []
def on_resp(r):
    if "json" in r.headers.get("content-type", ""):
        try: calls.append({"url": r.url, "status": r.status, "body": r.json()})
        except Exception: pass
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_context(storage_state="storage_state.json").new_page()
    page.on("response", on_resp)
    page.goto(sys.argv[1]); page.wait_for_load_state("networkidle"); page.wait_for_timeout(3000)
    open("page_dump.html", "w").write(page.content())
    json.dump(calls, open("api_dump.json", "w"), indent=1)
    print("final url:", page.url, "| wrote page_dump.html and api_dump.json,", len(calls), "JSON calls")
