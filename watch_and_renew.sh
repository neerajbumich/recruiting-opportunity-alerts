#!/usr/bin/env bash
# Run periodically by launchd while the Mac is on. Checks whether the cloud poller's
# last run reported an expired session; if so, pops open a real login window
# automatically (auto_login.py), waits for a human to sign in + approve Okta Verify,
# then uploads the new session and confirms the next cloud run works.
# Never proceeds past the point that needs a human tap — it just removes every step
# around that tap.
set -uo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
cd "$(dirname "$0")"
LOCK=/tmp/ross-alerts-renew.lock
LOG=watch_and_renew.log

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG"; }
notify() { osascript -e "display notification \"$2\" with title \"$1\"" >/dev/null 2>&1 || true; }

# Don't stack runs: if a previous login window is still open/waiting, leave it alone.
if [ -e "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
    log "already running (pid $(cat "$LOCK")), skipping this tick"
    exit 0
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

source .venv/bin/activate 2>/dev/null || { log "no .venv, aborting"; exit 1; }

if ! command -v gh >/dev/null; then
    log "ERROR: gh not found on PATH ($PATH) — cannot check status"
    notify "Ross Recruit watcher broken" "gh CLI not found — the check failed to run at all. Ask Claude to fix it."
    exit 1
fi
last_id=$(gh run list --workflow poll.yml --limit 1 --json databaseId -q '.[0].databaseId')
if [ -z "$last_id" ]; then
    log "ERROR: could not fetch last run id — gh auth or network problem"
    notify "Ross Recruit watcher broken" "Could not reach GitHub to check status."
    exit 1
fi
last_log=$(gh run view "$last_id" --log 2>&1)
if [ -z "$last_log" ]; then
    log "ERROR: gh run view returned nothing for run $last_id"
    notify "Ross Recruit watcher broken" "Could not read the run log — check manually."
    exit 1
fi
if ! echo "$last_log" | grep -q "session expired"; then
    log "session healthy, nothing to do"
    exit 0
fi

log "session expired detected — opening login window"
notify "Ross Recruit session expired" "A login window just opened — sign in and approve Okta Verify."

if ! python auto_login.py "https://michiganross.12twenty.com/events" >> "$LOG" 2>&1; then
    log "login timed out or failed — will retry next tick"
    notify "Ross Recruit renewal timed out" "Run ./renew.sh manually when you get a chance."
    exit 1
fi

python3 -c "import base64;print(base64.b64encode(open('storage_state.json','rb').read()).decode())" | gh secret set ROSS_STORAGE_STATE
gh workflow run poll.yml
sleep 8
run_id=$(gh run list --workflow poll.yml --limit 1 --json databaseId -q '.[0].databaseId')
gh run watch "$run_id" --exit-status >/dev/null 2>&1 || true

if gh run view "$run_id" --log 2>&1 | grep -q "session expired"; then
    log "renewal did not take — still reports expired"
    notify "Ross Recruit renewal failed" "Session still shows expired after a fresh login. Check manually."
    exit 1
fi

log "renewed successfully (run $run_id)"
notify "Ross Recruit renewed" "Session refreshed and confirmed working."
