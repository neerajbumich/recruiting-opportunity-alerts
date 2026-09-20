"""Run locally ONCE (and whenever the session expires). You sign in and approve
Okta Verify yourself; only the resulting browser session is saved."""
import base64, sys
from playwright.sync_api import sync_playwright

START = sys.argv[1] if len(sys.argv) > 1 else "https://REPLACE_ME"
with sync_playwright() as p:
    b = p.chromium.launch(headless=False)
    ctx = b.new_context()
    ctx.new_page().goto(START)
    input("Log in (incl. Okta Verify) in the browser, land on the Ross Recruit home page, then press Enter here... ")
    ctx.storage_state(path="storage_state.json")
    b.close()
enc = base64.b64encode(open("storage_state.json", "rb").read()).decode()
open("storage_state.b64", "w").write(enc)
print("Saved storage_state.json. For GitHub: gh secret set ROSS_STORAGE_STATE < storage_state.b64")
