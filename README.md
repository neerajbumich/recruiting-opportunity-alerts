# Ross Recruit alerts
1. `pip install -r requirements.txt && playwright install chromium`
2. `python login.py <ross-recruit-url>` – log in + Okta Verify yourself; saves the session.
3. `python inspect_page.py <events-url>` – look at page_dump.html, then fix URLs/selectors in config.yaml.
4. `python poll.py` locally (first run = baseline, no alerts). Set NTFY_TOPIC to test push (install the ntfy app, subscribe to a hard-to-guess topic).
5. Private GitHub repo: `gh secret set ROSS_STORAGE_STATE < storage_state.b64` (+ NTFY_TOPIC, SMTP_*, ALERT_EMAIL), push, enable Actions.
Notes: Actions cron can lag 5-15+ min; for truly real-time use a $5 VPS with cron/systemd. Re-run login.py when the session expires (you'll get an alert).
