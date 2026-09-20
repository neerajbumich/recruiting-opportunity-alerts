import base64, json, os, re, smtplib, sys
from email.message import EmailMessage
from pathlib import Path
import requests, yaml
from playwright.sync_api import sync_playwright

CFG = yaml.safe_load(open("config.yaml"))
SEEN = Path("seen.json")
seen = json.loads(SEEN.read_text()) if SEEN.exists() else None  # None => first run, baseline only

def notify(title, body, url=None):
    topic = os.environ.get("NTFY_TOPIC")
    if topic:
        h = {"Title": title}
        if url: h["Click"] = url
        requests.post(f"https://ntfy.sh/{topic}", data=body.encode(), headers=h, timeout=15)
    if os.environ.get("SMTP_HOST"):
        m = EmailMessage(); m["Subject"] = title
        m["From"] = os.environ["SMTP_USER"]; m["To"] = os.environ.get("ALERT_EMAIL", "neerajb@umich.edu")
        m.set_content(f"{body}\n\n{url or ''}")
        with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], 465) as s:
            s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"]); s.send_message(m)

def fetch(ctx, base, src):
    """Return {id: item}; raises PermissionError on expired session."""
    items, page = {}, 1
    while True:
        body = {**src["body"], "PageNumber": page}
        r = ctx.request.post(base + src["path"], data=body)
        if not r.ok or "json" not in r.headers.get("content-type", ""):
            raise PermissionError(r.status)
        j = r.json()
        for it in j["Items"]: items[it["Id"]] = it
        if page >= min(j["NumberOfPages"], src.get("max_pages", 10**6)): return items
        page += 1

def main():
    global seen
    if os.environ.get("TEST_EMAIL") == "1":
        notify("Ross Recruit alerts: test email", "If you can read this, email alerts are working."); print("test email sent"); return
    if not Path("storage_state.json").exists():
        Path("storage_state.json").write_bytes(base64.b64decode(os.environ["ROSS_STORAGE_STATE"]))
    if os.environ.get("SEND_ALL") == "1":
        base, lines = CFG["base_url"], []
        with sync_playwright() as p:
            ctx = p.chromium.launch().new_context(storage_state="storage_state.json")
            for src in CFG["sources"]:
                for it in fetch(ctx, base, src).values():
                    if any(str(it.get(f)) not in ok for f, ok in src.get("keep", {}).items()): continue
                    if any(str(it.get(f)) in bad for f, bad in src.get("exclude", {}).items()): continue
                    text = src["text"].format_map({k: it.get(k, "") for k in re.findall(r"{(\w+)}", src["text"])})
                    lines.append(f"[{src['name']}] {text}")
        notify(f"Ross Recruit: current snapshot ({len(lines)} items)", "\n".join(lines) + f"\n\n{base}")
        print(f"snapshot of {len(lines)} items sent"); return
    first_run, seen = seen is None, (seen or {})
    base, new = CFG["base_url"], []
    with sync_playwright() as p:
        ctx = p.chromium.launch().new_context(storage_state="storage_state.json")
        for src in CFG["sources"]:
            try: items = fetch(ctx, base, src)
            except PermissionError:
                notify("Ross Recruit session expired", "Run login.py locally and update the ROSS_STORAGE_STATE secret.")
                sys.exit(1)
            for id_, it in items.items():
                key = f"{src['name']}:{id_}"
                if key in seen: continue
                if any(str(it.get(f)) not in ok for f, ok in src.get("keep", {}).items()): continue
                if any(str(it.get(f)) in bad for f, bad in src.get("exclude", {}).items()): continue
                text = src["text"].format_map({k: it.get(k, "") for k in re.findall(r"{(\w+)}", src["text"])})
                seen[key] = text[:80]
                hay = " ".join(str(it.get(f, "")) for f in src["match_fields"]).lower()
                if not CFG.get("companies") or any(c.lower() in hay for c in CFG["companies"]):
                    new.append((src["name"], text, base + src["link"]))
        ctx.storage_state(path="storage_state.json")  # keep refreshed cookies
    SEEN.write_text(json.dumps(seen, indent=1))
    if first_run:
        print(f"Baseline saved ({len(seen)} items), no alerts sent."); return
    if new:
        lines = [f"[{name}] {text}\n  {href}" for name, text, href in new]
        n = len(new)
        notify(f"Ross Recruit: {n} new posting{'s' if n != 1 else ''}/event{'s' if n != 1 else ''}", "\n\n".join(lines))
    print(f"{len(new)} alert(s) sent.")

main()
