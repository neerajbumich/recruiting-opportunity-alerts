# Setup and operations

## Local setup

Use an isolated Python environment and install Chromium:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python login.py https://michiganross.12twenty.com/events
```

Complete login and MFA in the browser yourself. The script saves `storage_state.json` and its base64 representation. These contain authentication material and are ignored by Git. Page/API dumps and local logs are also ignored.

Review `config.yaml` before running. Portal-specific query IDs, work-authorization filters, job-status filters and watched event IDs reflect the configured recruiting context. They are not universal defaults.

`python poll.py` establishes a baseline when `seen.json` is absent. This repository includes existing state; use a separate private working copy with its own state for a new instance.

## Notifications and hosted execution

The workflow polls on a five-minute schedule, subject to GitHub scheduling delays. It can also run manually in snapshot or test-email mode. Those modes can send notifications immediately.

| Setting | Purpose |
| --- | --- |
| `ROSS_STORAGE_STATE` | Base64-encoded browser session for the cloud runner |
| `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` | Email delivery settings; the current implementation uses SMTP SSL on port 465 |
| `ALERT_EMAIL` | Recipients of opportunity notifications |
| `ADMIN_EMAIL` | Recipient of session-expiry email notices |
| `NTFY_TOPIC` | Optional push topic for local execution; not passed by the current workflow |

Store credentials in Actions secrets for a private live instance. The current workflow has configured email recipients rather than recipient secrets; review and replace them before deploying your own copy. `poll.py` also has a default email address when those settings are absent.

The optional ntfy path sends notifications, including maintenance notices, to the configured topic. The administrator-only distinction applies to email routing.

The workflow commits `seen.json` back to Git. It records short item labels as well as IDs, so review visibility before using the service with nonpublic portal data.

## Session renewal

`./renew.sh` opens a login browser, uploads the refreshed session secret, triggers a cloud poll and inspects the result. `watch_and_renew.sh` can be invoked by a local scheduler to detect an expired-session log and open the renewal flow. Both require local dependencies and an authenticated GitHub CLI. Running these scripts changes a repository secret and can trigger notifications.

## Operational limitations

- Event and posting queries depend on the current portal API shape.
- The posting query scans a bounded set of recent pages; it does not guarantee complete historical coverage.
- Changes to already recorded item IDs do not generate ordinary new-item alerts.
- Session-refresh cookies are saved locally on the runner; later cloud runs use the configured session secret.
- Delivery and state persistence are separate operations. Notification or Git-push failures need review; the workflow currently suppresses commit/push errors.
- A successful workflow is not proof that a notification reached or was read by its recipient.

Use the repository as an implementation reference. Do not run a configured live instance merely to preview the portfolio.
